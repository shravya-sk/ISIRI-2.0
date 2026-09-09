import webbrowser
from urllib.parse import quote


def execute(entities):
    action = entities.get("spotify_action")
    query = entities.get("query")

    # "Open Spotify" with no song mentioned - just launch it, no question asked
    if action == "open" and not query:
        url = "https://open.spotify.com"
        webbrowser.open(url)
        return {
            "success": True,
            "reply": "Opening Spotify...",
            "link": url,
        }

    # "Play a song" (or similar) with no title/artist given - ask for it
    if not query:
        return {
            "success": False,
            "reply": "What would you like me to search for on Spotify?",
        }

    encoded_query = quote(query)
    url = f"https://open.spotify.com/search/{encoded_query}"
    webbrowser.open(url)

    return {
        "success": True,
        "reply": f"Searching Spotify for {query}",
        "link": url,
    }