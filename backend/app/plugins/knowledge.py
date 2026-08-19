import requests
import re
from urllib.parse import quote

SEARCH_API = "https://en.wikipedia.org/w/api.php"
SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def execute(data):

    query = data.get("query", "").strip()

    if not query:
        return {
            "success": False,
            "reply": "I couldn't understand your question."
        }

    # Clean punctuation
    clean_query = re.sub(r"[^\w\s]", "", query).strip()

    try:
        # Search Wikipedia
        params = {
            "action": "opensearch",
            "search": clean_query,
            "limit": 5,
            "namespace": 0,
            "format": "json"
        }

        search_response = requests.get(
            SEARCH_API,
            params=params,
            headers={"User-Agent": "ISIRI-2.0"},
            timeout=10
        )

        search_response.raise_for_status()

        result = search_response.json()
        titles = result[1]

        if not titles:
            google_link = (
                "https://www.google.com/search?q="
                + quote(clean_query)
            )

            return {
                "success": True,
                "reply": f"I couldn't find a reliable summary for {clean_query}.",
                "link": google_link
            }

        # Use the closest Wikipedia result
        corrected_title = titles[0]

        # Get summary of THAT exact page
        summary_response = requests.get(
            SUMMARY_API + quote(corrected_title),
            headers={"User-Agent": "ISIRI-2.0"},
            timeout=10
        )

        summary_response.raise_for_status()

        summary_data = summary_response.json()

        summary = summary_data.get(
            "extract",
            f"I couldn't find a summary for {corrected_title}."
        )

        # Keep response short for ISIRI
        sentences = re.split(r'(?<=[.!?])\s+', summary)

        short_summary = " ".join(sentences[:3])

        # Google link uses the SAME corrected title
        google_link = (
            "https://www.google.com/search?q="
            + quote(corrected_title)
        )

        return {
            "success": True,
            "reply": short_summary,
            "link": google_link,
            "title": corrected_title
        }

    except Exception as e:

        return {
            "success": False,
            "reply": f"I couldn't retrieve information right now: {str(e)}",
            "link": None
        }