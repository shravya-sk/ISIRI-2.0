import re

def detect_intent(text):

    text = text.lower().strip()

    # Weather
    if re.search(
        r"\b(weather|temperature|forecast|rain|raining|humidity|wind)\b",
        text,
    ):
        return {"intent": "weather", "confidence": 0.95}

    # Alarm
    elif re.search(
        r"\b(alarm|remind me|wake me up|set a timer)\b",
        text,
    ):
        return {"intent": "alarm", "confidence": 0.95}

    # YouTube - checked BEFORE spotify, and matches "play/watch + youtube"
    # in EITHER word order (Tulu sentence structure often puts the verb
    # last: "youtube ... play", not just "play ... youtube"), OR
    # youtube+search/find together. Explicit "youtube" mention always
    # wins over the generic "song" trigger below.
    elif (
        re.search(r"\b(play|watch)\b.*\byoutube\b", text) or
        re.search(r"\byoutube\b.*\b(play|watch)\b", text) or
        (re.search(r"\byoutube\b", text) and re.search(r"\b(search|find)\b", text))
    ):
        return {"intent": "youtube", "confidence": 0.98}

    # Spotify - excludes sentences that also explicitly mention youtube,
    # since "song"/"music" alone shouldn't override an explicit platform name
    elif re.search(r"\b(spotify|song|music)\b", text) and "youtube" not in text:
        return {"intent": "spotify", "confidence": 0.95}

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
        r"camera|"
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

    # Device Control (lock)
    elif re.search(
        r"\b(lock|unlock|open|close)\b.*\b(door|lock|latch)\b|"
        r"\b(door|lock|latch)\b.*\b(lock|unlock|open|close)\b",
        text,
    ):
        return {"intent": "device_control", "confidence": 0.98}

    return {"intent": "unknown", "confidence": 0.0}