import re

def extract_entities(text):

    original_text = text.strip()      # Preserve original capitalization
    text = text.lower()

    entities = {}

    # --------------------------
    # Actor Detection
    # --------------------------

    actor_patterns = {
        "Shah Rukh Khan": [
            r"\bshahrukh\b",
            r"\bshah\s*rukh\b",
            r"\bsha\s*rukh\b",
            r"\bsrk\b"
        ],

        "Salman Khan": [
            r"\bsalman\b",
            r"\bsalman\s*khan\b"
        ],

        "Allu Arjun": [
            r"\ballu\b",
            r"\ballu\s*arjun\b"
        ]
    }

    for actor, patterns in actor_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text):
                entities["actor"] = actor
                break

    # --------------------------
    # Google Search Detection
    # --------------------------

    search_patterns = [
        r"search (.+)",
        r"google (.+)",
        r"find (.+)"
    ]

    for pattern in search_patterns:
        match = re.search(pattern, original_text, re.IGNORECASE)

        if match:
            entities["query"] = match.group(1).strip()
            break

    # --------------------------
    # YouTube Video Detection
    # --------------------------

    youtube_match = re.search(
        r"(?:play|watch)\s+(.+)",
        original_text,
        re.IGNORECASE
    )

    if youtube_match:
        entities["video"] = youtube_match.group(1).strip()


    # --------------------------
    # Website Detection
    # --------------------------

    websites = [
        "youtube",
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

    if any(word in text for word in ["today", "ivattu", "indu"]):
        entities["time"] = "today"

    elif any(word in text for word in ["tomorrow", "naale", "yelleda"]):
        entities["time"] = "tomorrow"

    return entities