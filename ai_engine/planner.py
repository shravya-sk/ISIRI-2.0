def plan(intent, entities):

    # intent is already a string
    intent_name = intent

    if intent_name == "weather":
        return {
            "plugin": "weather",
            "entities": entities
        }

    elif intent_name == "hardware":
        return {
            "plugin": "hardware",
            "entities": entities
        }

    elif intent_name == "movie_search":
        return {
            "plugin": "movies",
            "entities": entities
        }

    elif intent_name == "youtube":
        return {
            "plugin": "youtube",
            "entities": entities
        }

    elif intent_name == "system":
        return {
            "plugin": "system",
            "entities": entities
        }

    elif intent_name == "google_search":
        return {
            "plugin": "search",
            "entities": entities
        }

    elif intent_name == "browser":
        return {
            "plugin": "browser",
            "entities": entities
        }

    elif intent_name == "knowledge":
        return {
            "plugin": "knowledge",
            "entities": entities
        }

    elif intent_name == "calculator":
        return {
            "plugin": "calculator",
            "entities": entities
        }

    return {
        "plugin": None,
        "message": "Sorry, I don't know how to handle that request yet."
    }