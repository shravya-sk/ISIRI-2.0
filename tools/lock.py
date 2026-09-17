#!/usr/bin/env python3
"""
ISIRI 2.0 -- door lock command-line tool.

Drives the Raspberry Pi servo lock directly, with **no FastAPI, no uvicorn, no
Whisper and no torch** involved. It imports only backend/app/plugins/hardware.py,
which is deliberately standard-library-only, so this works even on a machine
where the backend's heavier dependencies are missing or the API routes are not
registering.

Use it to prove the tunnel + Pi + plugin chain independently of the web app:

    python tools/lock.py status
    python tools/lock.py unlock
    python tools/lock.py lock
    python tools/lock.py diag

Exits 0 on success and 1 on failure, so it can be used from a batch file.
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

# Load backend/.env the same way the backend does. If python-dotenv is missing
# we simply fall back to real environment variables -- this tool is meant to
# keep working on a half-installed machine.
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / "backend" / ".env")
    load_dotenv(ROOT / ".env")
except ImportError:
    print("note: python-dotenv not installed; using environment variables only\n",
          file=sys.stderr)

from app.plugins import hardware  # noqa: E402  (must follow the sys.path setup)


def _show_target() -> None:
    raw = os.environ.get("RPI_HOST", "")
    try:
        host, port = hardware.parse_rpi_host(raw)
        print("RPI_HOST : %s  ->  host=%s port=%d" % (raw or "(unset)", host, port))
    except ValueError as error:
        print("RPI_HOST : %s  ->  INVALID: %s" % (raw or "(unset)", error))
    print("mode     : %s" % ("SIMULATION" if os.environ.get(
        "HARDWARE_SIMULATION", "false").lower() == "true" else "real hardware"))
    print()


def cmd_status() -> int:
    _show_target()
    result = hardware.get_status()
    print("connected: %s" % ("yes" if result.get("rpi_connected") else "NO"))
    print("state    : %s" % result.get("state", "unknown"))
    if result.get("servo_mode"):
        print("servo    : %s" % result["servo_mode"])
    if result.get("error"):
        print("error    : %s" % result["error"])
    return 0 if result.get("success") else 1


def cmd_set(action: str) -> int:
    _show_target()
    result = hardware.control_hardware({"state": action})
    if result.get("success"):
        print("servo -> %s  (%s)" % (
            result.get("state"),
            "Pi confirmed" if result.get("rpi_connected") else "simulated"))
        return 0

    print("FAILED   : %s" % result.get("reply"))
    if result.get("error"):
        print("error    : %s" % result["error"])
    if result.get("hint"):
        print("hint     : %s" % result["hint"])
    return 1


def cmd_diag() -> int:
    report = hardware.diagnostics()
    print(json.dumps(report, indent=2, default=str))
    return 0 if report.get("reachable") else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Drive the ISIRI 2.0 Raspberry Pi door lock without the web backend.")
    parser.add_argument("command", choices=["status", "lock", "unlock", "diag"])
    parser.add_argument("--host", help="Override RPI_HOST, e.g. 127.0.0.1:5000 "
                                       "or [fe80::1%%wlan0]:5000")
    parser.add_argument("--timeout", help="Override RPI_TIMEOUT, in seconds")
    args = parser.parse_args()

    if args.host:
        os.environ["RPI_HOST"] = args.host
    if args.timeout:
        os.environ["RPI_TIMEOUT"] = args.timeout

    if args.command == "status":
        return cmd_status()
    if args.command == "diag":
        return cmd_diag()
    return cmd_set("locked" if args.command == "lock" else "unlocked")


if __name__ == "__main__":
    sys.exit(main())
