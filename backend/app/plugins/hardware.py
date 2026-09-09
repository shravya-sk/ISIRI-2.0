"""
ISIRI 2.0 -- Hardware Plugin (Door Lock)

Controls the servo-driven miniature door lock via HTTP calls to the
Raspberry Pi service (hardware/rpi_gpio_service.py).

Supported Commands:
- "Lock the door" / "Baakil lock malpule"
- "Unlock the door" / "Baakil unlock malpule"
"""

import logging
import os
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

RPI_HOST = os.environ.get("RPI_HOST", "http://127.0.0.1:5000")
HARDWARE_SIMULATION_MODE = os.environ.get("HARDWARE_SIMULATION", "true").lower() == "true"

LOCK_STATE = "locked"

TULU_RESPONSES = {
    "locked": "Baakil lock aathund.",
    "unlocked": "Baakil unlock aathund.",
}


def control_hardware(entities: Dict[str, Any]) -> Dict[str, Any]:
    global LOCK_STATE

    raw_action = str(entities.get("state", entities.get("action", "locked"))).lower().strip()

    if raw_action in {"lock", "locked", "close", "closed"}:
        action = "locked"
    elif raw_action in {"unlock", "unlocked", "open", "opened"}:
        action = "unlocked"
    else:
        action = "locked"

    LOCK_STATE = action
    logger.info(f"Hardware action: lock -> {action}")

    rpi_connected = False
    try:
        if not HARDWARE_SIMULATION_MODE:
            url = f"{RPI_HOST}/device/lock/{action}"
            res = requests.post(url, timeout=2.0)
            if res.status_code == 200:
                rpi_connected = True
    except Exception as e:
        logger.debug(f"RPi not reachable at {RPI_HOST}: {e}. Using simulated state.")

    tulu_reply = TULU_RESPONSES.get(action, f"Baakil {action}.")
    english_reply = f"The door is now {action}."

    return {
        "success": True,
        "reply": f"{english_reply} ({tulu_reply})",
        "device": "lock",
        "state": action,
        "rpi_connected": rpi_connected,
    }


def execute(data: Dict[str, Any]) -> Dict[str, Any]:
    return control_hardware(data)