import re


def detect_intent(text):

    text = text.lower()
    print("DEBUG:", text)

    # Weather
    if re.search(r"weather|temperature|rain|climate", text):
        return {
            "intent": "weather",
            "confidence": 0.9
        }


    # YouTube
    elif re.search(r"open|launch|go to", text):

        return {
            "intent": "browser",
            "confidence": 0.9
        }

    elif re.search(r"youtube|video|play|watch", text):

        return {
            "intent": "youtube",
            "confidence": 0.9
        }


    # Google Search
    elif re.search(r"search|google|find|who is|what is|tell me about", text):
        return {
            "intent": "google_search",
            "confidence": 0.8
        }


    # Movies
    elif re.search(r"movie|film|cinema", text):
        return {
            "intent": "movie_search",
            "confidence": 0.9
        }


    # Calculator
    elif re.search(r"calculate|plus|minus|multiply|divide", text):
        return {
            "intent": "calculator",
            "confidence": 0.9
        }


    else:
        return {
            "intent": "unknown",
            "confidence": 0
        }