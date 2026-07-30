import webbrowser

WEBSITES = {

    "youtube": "https://www.youtube.com",

    "instagram": "https://www.instagram.com",

    "gmail": "https://mail.google.com",

    "github": "https://github.com",

    "linkedin": "https://www.linkedin.com",

    "spotify": "https://open.spotify.com",

    "chatgpt": "https://chatgpt.com",

    "netflix": "https://www.netflix.com",

    "facebook": "https://www.facebook.com"
}


def execute(data):

    website = data.get("website")

    if not website:

        return {
            "success": False,
            "reply": "No website found."
        }

    webbrowser.open(WEBSITES[website])

    return {
        "success": True,
        "reply": f"Opening {website.title()}..."
    }