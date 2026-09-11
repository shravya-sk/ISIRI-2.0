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

    # YouTube search phrasing ("search/find X on youtube", "youtube search X")
    youtube_search_match = re.search(
        r"(?:search|find)\s+(.+?)\s+(?:on|in)\s+youtube|"
        r"youtube\s+(?:search|find)\s+(.+)",
        original_text,
        re.IGNORECASE
    )
    if youtube_search_match:
        captured = youtube_search_match.group(1) or youtube_search_match.group(2)
        if captured:
            entities["video"] = captured.strip().rstrip("?.!")

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

    if "spotify" in text:
        if re.search(r"\bopen\b", text) and not re.search(r"\b(play|song|music|track)\b", text):
            entities["spotify_action"] = "open"
        elif re.search(r"\b(play|song|music|track)\b", text):
            entities["spotify_action"] = "play"

    # --------------------------
    # Alarm Time Phrase Detection
    # --------------------------
    # Tries TWO word orders, since the trigger word ("alarm"/"remind me")
    # can come either before or after the actual time phrase depending on
    # phrasing/translation:
    #   "set an alarm for 6am tomorrow"   (trigger ... time)
    #   "10 second alarm delay"           (time ... trigger)
    # Picks whichever captured phrase actually contains a digit or a
    # recognizable time word, since that's the one likely to be real.

    TIME_HINT = re.compile(r"\d|noon|midnight|morning|evening|tonight|tomorrow|now", re.IGNORECASE)

    candidates = []

    after_match = re.search(
        r"(?:alarm|remind me|wake me up)\s*(?:for|at)?\s*(.+?)"
        r"(?:\s+because|\s+since|\s+so\b|\s+to\s+(?=[a-zA-Z])|,|$)",
        original_text,
        re.IGNORECASE
    )
    if after_match:
        candidates.append(after_match.group(1).strip().rstrip(".!?"))

    before_match = re.search(
        r"^(.*?)\s*(?:alarm|remind me|wake me up)",
        original_text,
        re.IGNORECASE
    )
    if before_match:
        candidates.append(before_match.group(1).strip().rstrip(".!?"))

    # Prefer a candidate that actually looks like a time expression
    chosen = None
    for c in candidates:
        if c and TIME_HINT.search(c):
            chosen = c
            break
    if not chosen and candidates and candidates[0]:
        chosen = candidates[0]

    if chosen:
        entities["alarm_time_text"] = chosen

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