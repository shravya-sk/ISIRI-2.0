import webbrowser
from yt_dlp import YoutubeDL


def execute(data):
    video = data.get("video")

    if not video:
        webbrowser.open("https://www.youtube.com")
        return {
            "success": True,
            "reply": "Opening YouTube..."
        }

    try:
        ydl_opts = {
            "quiet": True,
            "default_search": "ytsearch1"
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video, download=False)

            first_video = info["entries"][0]

            video_url = first_video["webpage_url"]

        webbrowser.open(video_url)

        return {
            "success": True,
            "reply": f"Playing {first_video['title']}"
        }

    except Exception as e:
        return {
            "success": False,
            "reply": str(e)
        }