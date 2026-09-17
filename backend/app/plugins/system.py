import os
import subprocess
from rapidfuzz import process

COMMON_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "explorer": "explorer.exe",
}

APP_PATHS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],

    "edge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],

    "code": [
        r"D:\Users\shrav\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        r"D:\Users\shrav\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd",
    ],

    "telegram": [
        os.path.expandvars(r"%AppData%\Telegram Desktop\Telegram.exe"),
    ],

    "discord": [
        os.path.expandvars(r"%LocalAppData%\Discord\Update.exe"),
    ],

    "spotify": [
        os.path.expandvars(r"%AppData%\Spotify\Spotify.exe"),
    ],

    # Some WhatsApp Desktop installs (non-Store version) use this path.
    # If not found, we fall back to the URI launch below.
    "whatsapp": [
        os.path.expandvars(r"%LocalAppData%\WhatsApp\WhatsApp.exe"),
    ],
}

# Apps that are best launched via their Windows URI protocol rather than
# guessing an .exe path - this covers built-in/Store apps (Camera,
# WhatsApp from Microsoft Store) where install paths vary a lot between
# machines and the protocol handler is far more reliable.
URI_APPS = {
    "camera": "microsoft.windows.camera:",
    "whatsapp": "whatsapp:",
}

ALL_APPS = {
    **COMMON_APPS,

    "chrome": "chrome",
    "google chrome": "chrome",

    "edge": "edge",

    "vs code": "code",
    "visual studio code": "code",
    "code": "code",

    "telegram": "telegram",

    "discord": "discord",

    "spotify": "spotify",

    "whatsapp": "whatsapp",

    "camera": "camera",
}


def execute(data):

    app = data.get("app")

    if not app:
        return {
            "success": False,
            "reply": "No application specified."
        }

    match = process.extractOne(app, ALL_APPS.keys())

    if not match or match[1] < 70:
        return {
            "success": False,
            "reply": f"I couldn't recognize {app}."
        }

    executable = ALL_APPS[match[0]]

    # Built-in Windows apps (notepad, calculator, etc.)
    if executable.endswith(".exe"):
        subprocess.Popen(executable)
        return {
            "success": True,
            "reply": f"Opening {match[0]}."
        }

    # Apps with a known .exe install path
    if executable in APP_PATHS:
        for path in APP_PATHS[executable]:
            if os.path.exists(path):
                subprocess.Popen(path)
                return {
                    "success": True,
                    "reply": f"Opening {match[0]}."
                }

    # Fall back to URI protocol launch (Camera, Store-installed WhatsApp)
    if executable in URI_APPS:
        try:
            os.startfile(URI_APPS[executable])
            return {
                "success": True,
                "reply": f"Opening {match[0]}."
            }
        except OSError as e:
            return {
                "success": False,
                "reply": f"Couldn't open {match[0]}: {e}"
            }

    return {
        "success": False,
        "reply": f"{match[0]} is not installed or its path couldn't be found."
    }