import re

def detect_intent(text):
    text = text.lower()

    # ----------------------------
    # TURN ON LIGHT
    # ----------------------------
    if (
        (re.search(r"\b(light|bulb|lamp)\b", text) and "on" in text)
        or ("bulb" in text and "malpule" in text)
    ):
        return {
            "intent": "TURN_ON_LIGHT",
            "entities": {
                "device": "light"
            }
        }

    # ----------------------------
    # TURN OFF LIGHT
    # ----------------------------
    if (
        (re.search(r"\b(light|bulb|lamp)\b", text) and "off" in text)
        or ("bulb" in text and "off" in text)
    ):
        return {
            "intent": "TURN_OFF_LIGHT",
            "entities": {
                "device": "light"
            }
        }

    # ----------------------------
    # WEATHER
    # ----------------------------
    if "weather" in text:
        return {
            "intent": "GET_WEATHER",
            "entities": {}
        }

    # ----------------------------
    # YOUTUBE
    # ----------------------------
    if "youtube" in text:
        return {
            "intent": "OPEN_YOUTUBE",
            "entities": {}
        }

    return {
        "intent": "UNKNOWN",
        "entities": {}
    }