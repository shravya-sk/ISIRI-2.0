"""
ISIRI 2.0 — Raspberry Pi GPIO Hardware Service Daemon

This standalone daemon runs directly on a Raspberry Pi.
It listens for HTTP REST commands from ISIRI 2.0 backend and controls physical GPIO pins
connected to relays, LEDs, or home appliances.

Pin Mapping (BCM numbering):
- GPIO 17 (Pin 11): Light (Relay Channel 1 / LED)
- GPIO 27 (Pin 13): Fan (Relay Channel 2 / LED)
- GPIO 22 (Pin 15): Geyser / AC (Relay Channel 3)
- GPIO 23 (Pin 16): Auxiliary / Socket (Relay Channel 4)

Endpoints:
- GET  /status                  -> Returns current GPIO states
- POST /device/{device}/{state} -> Sets device to 'on' or 'off'

Usage on Raspberry Pi:
    python hardware/rpi_gpio_service.py --port 5000
"""

import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RPi-GPIO-Service")

# Pin configuration
GPIO_PINS = {
    "light": 17,
    "fan": 27,
    "geyser": 22,
    "ac": 22,
    "socket": 23
}

DEVICE_STATES = {
    "light": False,
    "fan": False,
    "geyser": False,
    "ac": False,
    "socket": False
}

# Attempt to load RPi.GPIO or fallback to simulation
HAVE_RPI_GPIO = False
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in set(GPIO_PINS.values()):
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    HAVE_RPI_GPIO = True
    logger.info("✅ Physical RPi.GPIO initialized successfully.")
except (ImportError, RuntimeError):
    logger.info("ℹ️  Running in hardware SIMULATION mode (RPi.GPIO not detected).")


def set_pin_state(device: str, state_str: str) -> bool:
    device = device.lower().strip()
    if device not in GPIO_PINS:
        return False

    is_on = (state_str.lower().strip() == "on")
    DEVICE_STATES[device] = is_on

    pin = GPIO_PINS[device]
    if HAVE_RPI_GPIO:
        GPIO.output(pin, GPIO.HIGH if is_on else GPIO.LOW)
        logger.info(f"GPIO Pin {pin} ({device}) set to {'HIGH (ON)' if is_on else 'LOW (OFF)'}")
    else:
        logger.info(f"[SIMULATION] Device '{device}' (Pin {pin}) -> {'ON' if is_on else 'OFF'}")

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
                "service": "ISIRI 2.0 Raspberry Pi GPIO Daemon",
                "hardware_mode": "physical" if HAVE_RPI_GPIO else "simulation",
                "pin_mapping": GPIO_PINS,
                "states": {k: "on" if v else "off" for k, v in DEVICE_STATES.items()}
            })
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        parts = [p for p in self.path.strip("/").split("/") if p]
        # Expected format: /device/{device_name}/{action}
        if len(parts) == 3 and parts[0] == "device":
            device = parts[1]
            action = parts[2]
            success = set_pin_state(device, action)
            if success:
                self._send_json(200, {
                    "success": True,
                    "device": device,
                    "state": action,
                    "pin": GPIO_PINS.get(device)
                })
            else:
                self._send_json(400, {"success": False, "error": f"Unknown device: {device}"})
        else:
            self._send_json(400, {"error": "Invalid endpoint format. Use /device/{name}/{on|off}"})


def run_server(port: int = 5000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, RequestHandler)
    logger.info(f"🚀 ISIRI 2.0 GPIO Service listening on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down GPIO service...")
    finally:
        if HAVE_RPI_GPIO:
            GPIO.cleanup()
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ISIRI 2.0 Raspberry Pi GPIO Daemon")
    parser.add_argument("--port", type=int, default=5000, help="HTTP server port")
    args = parser.parse_args()
    run_server(args.port)
