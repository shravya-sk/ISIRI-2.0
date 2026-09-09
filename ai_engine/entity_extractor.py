import re
from rapidfuzz import process


def extract_entities(text):

    original_text = text.strip()      # Preserve original capitalization
    text = text.lower()

    entities = {}

    # --------------------------
    # Actor Detection
    # --------------------------

    patterns = [
        r"who\s+is\s+(.+)",
        r"who\s+was\s+(.+)",
        r"what\s+is\s+(.+)",
        r"tell\s+me\s+about\s+(.+)",
        r"information\s+about\s+(.+)",
        r"describe\s+(.+)",
        r"explain\s+(.+)",
        r"^is(.+)",
        r"^o\s+(.+)",
        r"^oh\s+(.+)",
        r"^hui\s+(.+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            query = re.sub(r"^[^\w]+", "", query)
            query = query.replace("-", " ")
            entities["query"] = query
            break

    # --------------------------
    # Google Search Detection
    # --------------------------

    search_patterns = [
        r"search (.+)",
        r"google (.+)",
        r"find (.+)",
        r"who is (.+)",
        r"what is (.+)",
        r"who was (.+)",
        r"where is (.+)",
        r"when is (.+)",
        r"tell me about (.+)"
    ]

    for pattern in search_patterns:
        match = re.search(pattern, original_text, re.IGNORECASE)
        if match:
            entities["query"] = match.group(1).strip().rstrip("?")
            break

    # --------------------------
    # YouTube Video Detection
    # --------------------------

    youtube_match = re.search(
        r"(?:play|watch)\s+(.+?)(?:\s+on\s+youtube)?$",
        original_text,
        re.IGNORECASE
    )

    if youtube_match:
        entities["video"] = youtube_match.group(1).strip()

    # --------------------------
    # Spotify Search Detection
    # --------------------------

    spotify_match = re.search(
        r"(?:search|find)\s+(.+?)\s+(?:on|in)\s+spotify",
        original_text,
        re.IGNORECASE
    )

    if spotify_match:
        entities["query"] = spotify_match.group(1).strip()

    # --------------------------
    # Spotify Open vs Play Detection
    # --------------------------
    # Distinguishes "open spotify" (just launch it) from "play a song on
    # spotify" (needs a title/artist - ask if not given).

    if "spotify" in text:
        if re.search(r"\bopen\b", text) and not re.search(r"\b(play|song|music|track)\b", text):
            entities["spotify_action"] = "open"
        elif re.search(r"\b(play|song|music|track)\b", text):
            entities["spotify_action"] = "play"

    # --------------------------
    # Website Detection
    # --------------------------

    websites = [
        "youtube",
        "google",
        "instagram",
        "gmail",
        "github",
        "linkedin",
        "spotify",
        "chatgpt",
        "netflix",
        "facebook"
    ]

    for site in websites:
        if site in text:
            entities["website"] = site
            break

    system_match = re.search(
        r"open\s+(.+)",
        original_text,
        re.IGNORECASE
    )

    if system_match:
        entities["app"] = system_match.group(1).strip()


    # --------------------------
    # Alarm Time Phrase Detection
    # --------------------------
    alarm_time_match = re.search(
        r"(?:alarm|remind me|wake me up)\s*(?:for|at)?\s*(.+?)"
        r"(?:\s+because|\s+since|\s+so\b|,|$)",
        original_text,
        re.IGNORECASE
    )
    if alarm_time_match:
        entities["alarm_time_text"] = alarm_time_match.group(1).strip()

        
    # --------------------------
    # Weather Location Detection
    # --------------------------

    weather_location_patterns = [
        r"\b(?:weather(?:\s+forecast)?|temperature|forecast|rain(?:ing)?|humidity|wind)"
        r"\s+(?:in|for|at)\s+([a-zA-Z][a-zA-Z\s-]*?)(?:\s+(?:today|tomorrow))?[?.!]*$",

        r"\b(?:in|for|at)\s+([a-zA-Z][a-zA-Z\s-]*?)"
        r"\s+(?:weather|temperature|forecast|rain)\b",
    ]

    for pattern in weather_location_patterns:
        match = re.search(pattern, original_text, re.IGNORECASE)
        if match:
            location = match.group(1).strip().rstrip("?.!, ")
            entities["location"] = location.title()
            break

    # --------------------------
    # Time Detection
    # --------------------------

    if any(word in text for word in ["today", "ini"]):
        entities["time"] = "today"
    elif any(word in text for word in ["tomorrow", "yelle", "yelle da"]):
        entities["time"] = "tomorrow"

    # --------------------------
    # Device Lock Detection (separate from time - not an elif on it)
    # --------------------------

    if re.search(r"\b(door|lock|latch)\b", text):
        entities["device"] = "lock"

    if re.search(r"\b(lock|locked)\b", text) and "unlock" not in text:
        entities["state"] = "locked"
    elif re.search(r"\b(unlock|unlocked|open)\b", text):
        entities["state"] = "unlocked"

    return entities