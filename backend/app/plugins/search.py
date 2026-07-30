import webbrowser
import urllib.parse

def execute(data):
    query = data.get("query", "")

    if not query:
        return {
            "success": False,
            "reply": "No search query found."
        }

    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)

    webbrowser.open(url)

    return {
        "success": True,
        "reply": f"Searching Google for {query}"
    }