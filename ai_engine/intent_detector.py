import re

def detect_intent(text):

    text = text.lower().strip()

    # Weather
    if re.search(
        r"\b(weather|temperature|forecast|rain|raining|humidity|wind)\b",
        text,
    ):
        return {"intent": "weather", "confidence": 0.95}

    # Hardware / Home Automation (Light, Fan, AC, Geyser, etc.)
    elif re.search(
        r"\b(turn\s+on|turn\s+off|switch\s+on|switch\s+off)\b.*\b(light|lights|fan|fans|bulb|lamp|geyser|ac|tv|socket|device)\b|"
        r"\b(light|lights|fan|fans|bulb|lamp|geyser|ac|tv)\b.*\b(turn\s+on|turn\s+off|switch\s+on|switch\s+off|on|off)\b",
        text,
    ):
        return {"intent": "hardware", "confidence": 0.98}

    # Spotify
    elif re.search(r"\b(spotify|song|music)\b", text):
        return {"intent": "spotify", "confidence": 0.95}
    
    # YouTube
    elif re.search(r"\b(play|watch)\b.*\b(on\s+)?youtube\b", text):
        return {"intent": "youtube", "confidence": 0.98}

    # Open Websites
    elif re.search(
        r"\bopen\b.*\b(youtube|instagram|gmail|github|linkedin|spotify|chatgpt|netflix|facebook|google)\b",
        text
    ):
        return {"intent": "browser", "confidence": 0.98}

    # Desktop Applications
    elif re.search(
        r"\bopen\b.*\b("
        r"notepad|calculator|calc|paint|"
        r"chrome|google chrome|"
        r"telegram|discord|"
        r"word|excel|powerpoint|"
        r"vs code|vscode|visual studio code|code|"
        r"pycharm|"
        r"steam|vlc|obs|"
        r"whatsapp|"
        r"edge|firefox|brave|"
        r"cmd|terminal|"
        r"explorer|file explorer"
        r")\b",
        text
    ):
        return {"intent": "system", "confidence": 0.98}

    # Google Search
    elif re.search(r"\b(search|google|find)\b", text):
        return {"intent": "google_search", "confidence": 0.95}

    # Knowledge
    elif re.search(
        r"(who\s+is|who\s+was|what\s+is|tell\s+me\s+about|describe|explain|information\s+about)",
        text
    ):
        return {"intent": "knowledge", "confidence": 0.90}

    # Calculator
    elif re.search(r"\b(calculate|plus|minus|multiply|divide)\b", text):
        return {"intent": "calculator", "confidence": 0.95}

    return {"intent": "unknown", "confidence": 0.0}