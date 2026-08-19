import webbrowser
from urllib.parse import quote


def execute(data):

    query = data.get("video", "")

    if not query:
        return {
            "success": False,
            "reply": "What would you like me to play?"
        }

    url = f"https://www.youtube.com/results?search_query={quote(query)}"

    webbrowser.open(url)

    return {
        "success": True,
        "reply": f"Playing {query} on YouTube."
    }