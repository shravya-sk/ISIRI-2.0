"""
ISIRI 2.0 — Raspberry Pi Servo Lock Service Daemon

Standalone daemon that runs on the Raspberry Pi. Listens for HTTP commands
from the ISIRI 2.0 backend and drives an SG90 servo to lock/unlock a
3D-printed rack-and-pinion latch.

Hardware note: the built mechanism is a rack-and-pinion, not a simple flip
latch. The servo horn carries a pinion gear that meshes with a toothed
rack bar; rotating the servo drives the rack linearly to extend/retract
the bolt. Because the rack needs its full travel, the servo sweeps the
full 0-180 degree range (not the smaller 0-90 range a flip latch would
need). CALIBRATE the two endpoint angles below once mounted, since the
direction (which end is "locked") depends on how the pinion meshes with
the rack on your print.

Networking note: this daemon binds "::" as a DUAL-STACK socket, so it
answers on IPv6 (including link-local fe80:: addresses) *and* IPv4 on the
same port. The stdlib HTTPServer defaults to IPv4-only, which is why the
backend could never reach the Pi on networks where only IPv6 works.

Pin Mapping (BCM numbering):
- GPIO 18 (Pin 12): Door Lock Servo (PWM signal pin)

Endpoints:
- GET  /status                 -> Returns current lock state
- POST /device/lock/{state}    -> state = 'locked' or 'unlocked'
- GET  /device/lock/{state}    -> same, so it can be tested from a browser

Usage on Raspberry Pi:
    python3 hardware/rpi_gpio_service.py --port 5000
"""

import argparse
import json
import logging
import socket
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RPi-Lock-Service")

LOCK_SERVO_PIN = 18   # BCM 18 = hardware PWM capable, good choice for servo

# Rack-and-pinion needs the servo's full sweep to drive the rack all the way
# in/out. Swap these two values if your mechanism ends up locking backwards.
LOCK_ANGLE = 180      # servo angle when locked (rack fully driven one way) - CALIBRATE
UNLOCK_ANGLE = 0      # servo angle when unlocked (rack fully driven back)  - CALIBRATE

LOCK_STATE = "locked"  # in-memory current state

# Attempt to load gpiozero for the servo; fall back to simulation if unavailable
HAVE_SERVO = False
lock_servo = None
try:
    from gpiozero import AngularServo
    lock_servo = AngularServo(
        LOCK_SERVO_PIN,
        min_angle=0,
        max_angle=180,
        min_pulse_width=0.0005,   # ~0.5ms - typical for 180° SG90s; fine-tune if it buzzes at the ends
        max_pulse_width=0.0025,   # ~2.5ms
    )
    lock_servo.angle = LOCK_ANGLE  # start locked
    HAVE_SERVO = True
    logger.info("Physical servo initialized on GPIO %s.", LOCK_SERVO_PIN)
except Exception as e:
    logger.info("Running in SIMULATION mode (servo not detected: %s).", e)


def set_lock_state(state_str: str) -> bool:
    """Moves the servo to lock or unlock the latch. Accepts 'locked' or 'unlocked'."""
    global LOCK_STATE

    state_str = state_str.lower().strip()
    if state_str not in {"locked", "unlocked"}:
        logger.warning("Unrecognized lock state '%s', ignoring.", state_str)
        return False

    LOCK_STATE = state_str
    target_angle = LOCK_ANGLE if state_str == "locked" else UNLOCK_ANGLE

    if HAVE_SERVO:
        lock_servo.angle = target_angle
        logger.info("Servo moved to %s degrees (%s)", target_angle, state_str)
    else:
        logger.info("[SIMULATION] Lock -> %s (would move servo to %s degrees)", state_str, target_angle)

    return True


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "ISIRI-Lock/2.0"

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(body)

    def _status_payload(self) -> dict:
        return {
            "service": "ISIRI 2.0 Raspberry Pi Servo Lock Daemon",
            "servo_mode": "physical" if HAVE_SERVO else "simulation",
            "pin": LOCK_SERVO_PIN,
            "state": LOCK_STATE,
        }

    def _handle_lock_path(self) -> bool:
        """Handles /device/lock/{state}. Returns True if the path was ours."""
        parts = [p for p in self.path.split("?")[0].strip("/").split("/") if p]
        if len(parts) == 3 and parts[0] == "device" and parts[1] == "lock":
            action = parts[2].lower().strip()
            if set_lock_state(action):
                self._send_json(200, {"success": True, "device": "lock", "state": action})
            else:
                self._send_json(400, {"success": False, "error": f"Invalid state: {action}"})
            return True
        return False

    def do_OPTIONS(self):
        self._send_json(204, {})

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ["/", "/status"]:
            self._send_json(200, self._status_payload())
        elif self._handle_lock_path():
            # Convenience: lets you drive the lock straight from a browser bar.
            return
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        if not self._handle_lock_path():
            self._send_json(400, {"error": "Invalid endpoint. Use /device/lock/{locked|unlocked}"})

    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)


class DualStackHTTPServer(ThreadingHTTPServer):
    """IPv6 server with IPV6_V6ONLY cleared, so one socket serves IPv6 + IPv4.

    The stdlib HTTPServer hardcodes address_family = AF_INET (IPv4 only). That is
    why an IPv6-only path to the Pi could never reach this daemon, even though
    ssh (which listens on ::) worked fine.
    """

    address_family = socket.AF_INET6
    allow_reuse_address = True
    daemon_threads = True

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError) as e:
            # Some systems refuse to clear V6ONLY; we still serve IPv6.
            logger.warning("Could not enable dual-stack (IPv4 clients may not reach us): %s", e)
        super().server_bind()


class IPv4HTTPServer(ThreadingHTTPServer):
    """Fallback for hosts with IPv6 disabled entirely."""

    allow_reuse_address = True
    daemon_threads = True


def _ip_addrs(family: str, *filters) -> list:
    """Parses `ip -o <family> addr show <filters>`. Returns [(iface, address), ...]."""
    try:
        out = subprocess.run(
            ["ip", "-o", family, "addr", "show"] + list(filters),
            capture_output=True, text=True, timeout=3,
        ).stdout
    except Exception:
        return []

    found = []
    for line in out.splitlines():
        fields = line.split()
        # e.g. "2: wlan0    inet6 fe80::1/64 scope link ..."
        if len(fields) < 4:
            continue
        iface = fields[1]
        for i, token in enumerate(fields):
            if token in ("inet", "inet6") and i + 1 < len(fields):
                found.append((iface, fields[i + 1].split("/")[0]))
                break
    return found


def log_connection_hints(port: int) -> None:
    """Prints copy-pasteable RPI_HOST values so the backend can be pointed here."""
    logger.info("-" * 64)
    logger.info("Set one of these as RPI_HOST in the ISIRI backend's .env file:")

    printed = False

    for iface, addr in _ip_addrs("-6", "scope", "global"):
        logger.info("  RPI_HOST=[%s]:%s        (global IPv6 via %s)", addr, port, iface)
        printed = True

    for iface, addr in _ip_addrs("-6", "scope", "link"):
        logger.info("  RPI_HOST=[%s%%ZONE]:%s  (link-local IPv6 via %s)", addr, port, iface)
        logger.info("      ^ replace ZONE with YOUR PC's interface, not the Pi's:")
        logger.info("        Linux/macOS -> the name, e.g. %s", "%wlan0")
        logger.info("        Windows     -> the numeric Idx from: netsh interface ipv6 show interfaces")
        printed = True

    for iface, addr in _ip_addrs("-4"):
        if addr.startswith("127."):
            continue
        logger.info("  RPI_HOST=%s:%s             (IPv4 via %s)", addr, port, iface)
        printed = True

    if not printed:
        logger.info("  (could not enumerate addresses - run `ip addr` manually)")
    logger.info("-" * 64)


def run_server(port: int = 5000, host: str = "::"):
    httpd = None
    try:
        httpd = DualStackHTTPServer((host, port), RequestHandler)
        logger.info("Bound [%s]:%s (dual-stack: IPv6 + IPv4).", host, port)
    except OSError as e:
        logger.warning("IPv6 bind on [%s]:%s failed (%s); falling back to IPv4-only.", host, port, e)
        # Honour an explicitly requested IPv4 address; otherwise listen on all.
        ipv4_host = host if host not in ("::", "") else "0.0.0.0"
        try:
            httpd = IPv4HTTPServer((ipv4_host, port), RequestHandler)
        except OSError:
            ipv4_host = "0.0.0.0"
            httpd = IPv4HTTPServer((ipv4_host, port), RequestHandler)
        logger.info("Bound %s:%s (IPv4 only).", ipv4_host, port)

    log_connection_hints(port)
    logger.info("ISIRI 2.0 Lock Service listening on port %s...", port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down lock service...")
    finally:
        if HAVE_SERVO and lock_servo is not None:
            lock_servo.detach()
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ISIRI 2.0 Raspberry Pi Servo Lock Daemon")
    parser.add_argument("--port", type=int, default=5000, help="HTTP server port")
    parser.add_argument("--host", default="::", help="Bind address (default :: = all, dual-stack)")
    args = parser.parse_args()
    run_server(args.port, args.host)
