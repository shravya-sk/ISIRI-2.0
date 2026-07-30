from app.plugins import (
    weather,
    search,
    youtube,
    movies,
    calculator,
    translation
)

def execute(intent, entities):

    if intent == "GET_WEATHER":
        return weather.execute(entities)

    elif intent == "WEB_SEARCH":
        return search.execute(entities)

    elif intent == "OPEN_YOUTUBE":
        return youtube.execute(entities)

    elif intent == "SEARCH_MOVIES":
        return movies.execute(entities)

    elif intent == "CALCULATE":
        return calculator.execute(entities)

    elif intent == "TRANSLATE":
        return translation.execute(entities)

    return {
        "success": False,
        "reply": "Sorry, I don't understand that command."
    }