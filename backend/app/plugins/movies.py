def execute(data):
    actor = data.get("actor", "")

    return {
        "success": True,
        "reply": f"Searching movies of {actor}..."
    }