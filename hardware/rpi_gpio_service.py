"""
ISIRI 2.0 — Raspberry Pi Servo Lock Service Daemon

Standalone daemon that runs on the Raspberry Pi. Listens for HTTP commands
from the ISIRI 2.0 backend and drives an SG90 servo to lock/unlock a
miniature 3D-printed latch.

Pin Mapping (BCM numbering):
- GPIO 18 (Pin 12): Door Lock Servo (PWM signal pin)

Endpoints:
- GET  /status                 -> Returns current lock state
- POST /device/lock/{state}    -> state = 'locked' or 'unlocked'

Usage on Raspberry Pi:
    python hardware/rpi_gpio_service.py --port 5000
"""

import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RPi-Lock-Service")

LOCK_SERVO_PIN = 18   # BCM 18 = hardware PWM capable, good choice for servo
LOCK_ANGLE = 0        # servo angle when locked - CALIBRATE once mounted on your latch
UNLOCK_ANGLE = 90     # servo angle when unlocked - CALIBRATE once mounted on your latch

LOCK_STATE = "locked"  # in-memory current state

# Attempt to load gpiozero for the servo; fall back to simulation if unavailable
HAVE_SERVO = False
lock_servo = None
try:
    from gpiozero import AngularServo
    lock_servo = AngularServo(
        LOCK_SERVO_PIN,
        min_angle=0,
        max_angle=90,
        min_pulse_width=0.0006,
        max_pulse_width=0.0023,
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
    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        if self.path in ["/", "/status"]:
            self._send_json(200, {
                "service": "ISIRI 2.0 Raspberry Pi Servo Lock Daemon",
                "servo_mode": "physical" if HAVE_SERVO else "simulation",
                "pin": LOCK_SERVO_PIN,
                "state": LOCK_STATE,
            })
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        parts = [p for p in self.path.strip("/").split("/") if p]
        # Expected format: /device/lock/{state}
        if len(parts) == 3 and parts[0] == "device" and parts[1] == "lock":
            action = parts[2].lower().strip()
            success = set_lock_state(action)
            if success:
                self._send_json(200, {"success": True, "device": "lock", "state": action})
            else:
                self._send_json(400, {"success": False, "error": f"Invalid state: {action}"})
        else:
            self._send_json(400, {"error": "Invalid endpoint. Use /device/lock/{locked|unlocked}"})


def run_server(port: int = 5000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, RequestHandler)
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
    args = parser.parse_args()
    run_server(args.port)