import webbrowser
from urllib.parse import quote


def execute(entities):
    query = entities.get("query")

    if not query:
        return {
            "success": False,
            "reply": "What would you like me to search for on Spotify?"
        }

    encoded_query = quote(query)

    url = f"https://open.spotify.com/search/{encoded_query}"

    webbrowser.open(url)

    return {
        "success": True,
        "reply": f"Searching Spotify for {query}",
        "link": url
    }