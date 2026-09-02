import re
from rapidfuzz import process

def extract_entities(text):

    original_text = text.strip()      # Preserve original capitalization
    text = text.lower()

    entities = {}

    # --------------------------
    # Hardware & Appliance Entities
    # --------------------------
    # Device State
    if re.search(r"\b(turn\s+on|switch\s+on|\bon\b)\b", text):
        entities["state"] = "on"
    elif re.search(r"\b(turn\s+off|switch\s+off|\boff\b)\b", text):
        entities["state"] = "off"

    # Device Type
    if re.search(r"\b(fan|fans)\b", text):
        entities["device"] = "fan"
    elif re.search(r"\b(light|lights|bulb|bulbs|lamp|lamps|tube\s*light)\b", text):
        entities["device"] = "light"
    elif re.search(r"\b(geyser|water\s+heater|heater)\b", text):
        entities["device"] = "geyser"
    elif re.search(r"\b(ac|air\s+conditioner)\b", text):
        entities["device"] = "ac"
    elif re.search(r"\b(tv|television)\b", text):
        entities["device"] = "tv"

    # Room Location
    rooms = ["bedroom", "living room", "hall", "kitchen", "porch", "balcony", "corridor", "bathroom", "garage"]
    for r in rooms:
        if r in text:
            entities["room"] = r
            break

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
    # Location Detection
    # --------------------------

    locations = [
        "mangalore",
        "bangalore",
        "bengaluru",
        "udupi",
        "mysore",
        "mumbai",
        "delhi"
    ]

    for location in locations:
        if location in text:
            entities["location"] = location.title()

    # --------------------------
    # Time Detection
    # --------------------------

    if any(word in text for word in ["today", "ini"]):
        entities["time"] = "today"
    elif any(word in text for word in ["tomorrow", "yelle", "yelle da"]):
        entities["time"] = "tomorrow"

    return entities