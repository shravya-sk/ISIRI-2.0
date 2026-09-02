"""
ISIRI 2.0 — Hardware & Home Automation Plugin

Controls IoT relays, LEDs, and appliances (Lights, Fans, etc.)
via local GPIO on Raspberry Pi or HTTP REST/MQTT network calls.

Supported Commands:
- "Turn on the light" / "Light on malpule"
- "Turn off the light" / "Light off malpule"
- "Turn on the fan" / "Fan on malpule"
- "Turn off the fan" / "Fan off malpule"
"""

import logging
import os
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Configurable Raspberry Pi IP / URL (default: localhost or local network RPi IP)
RPI_HOST = os.environ.get("RPI_HOST", "http://127.0.0.1:5000")
HARDWARE_SIMULATION_MODE = os.environ.get("HARDWARE_SIMULATION", "true").lower() == "true"

# Local in-memory state for development / fallback simulation
DEVICE_STATES = {
    "light": "off",
    "fan": "off",
    "geyser": "off",
    "ac": "off",
    "tv": "off"
}

# Tulu response templates for hardware
TULU_RESPONSES = {
    ("light", "on"): "Light on aathund.",
    ("light", "off"): "Light off aathund.",
    ("fan", "on"): "Fan on aathund.",
    ("fan", "off"): "Fan off aathund.",
    ("default", "on"): "{device} on aathund.",
    ("default", "off"): "{device} off aathund."
}


def control_hardware(entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a hardware control command based on extracted entities.
    
    Entities expected:
    - device: 'light', 'fan', 'bulb', 'ac', 'geyser', etc.
    - state: 'on' or 'off'
    - room: 'bedroom', 'hall', 'kitchen' (optional)
    """
    device = str(entities.get("device", "light")).lower().strip()
    action = str(entities.get("state", entities.get("action", "on"))).lower().strip()
    room = str(entities.get("room", "")).strip()

    # Normalize device names
    if "fan" in device:
        device = "fan"
    elif any(k in device for k in ["light", "bulb", "lamp", "led"]):
        device = "light"
    elif any(k in device for k in ["geyser", "heater"]):
        device = "geyser"
    elif "ac" in device:
        device = "ac"

    if action not in {"on", "off", "toggle"}:
        action = "on"

    if action == "toggle":
        current = DEVICE_STATES.get(device, "off")
        action = "off" if current == "on" else "on"

    # 1. Update local simulation state
    DEVICE_STATES[device] = action
    logger.info(f"Hardware action: {device} -> {action} (room: {room})")

    # 2. Attempt network call to Raspberry Pi if active
    rpi_connected = False
    try:
        if not HARDWARE_SIMULATION_MODE:
            url = f"{RPI_HOST}/device/{device}/{action}"
            res = requests.post(url, json={"room": room}, timeout=2.0)
            if res.status_code == 200:
                rpi_connected = True
    except Exception as e:
        logger.debug(f"RPi not reachable at {RPI_HOST}: {e}. Using simulated state.")

    # 3. Construct user response
    resp_key = (device, action)
    if resp_key in TULU_RESPONSES:
        tulu_reply = TULU_RESPONSES[resp_key]
    else:
        tulu_reply = TULU_RESPONSES.get((f"default", action), f"{device.title()} turned {action}.").format(device=device)

    room_text = f" in the {room}" if room else ""
    english_reply = f"{device.title()}{room_text} is turned {action}."

    return {
        "success": True,
        "reply": f"{english_reply} ({tulu_reply})",
        "device": device,
        "state": action,
        "room": room,
        "rpi_connected": rpi_connected,
        "device_states": DEVICE_STATES.copy()
    }


def execute(data: Dict[str, Any]) -> Dict[str, Any]:
    """Standard ISIRI plugin execution entrypoint."""
    return control_hardware(data)
