from pathlib import Path

# Load .env FIRST: the plugins read their configuration (RPI_HOST,
# HARDWARE_SIMULATION, ...) at import time, so this has to happen before any
# backend.app.* import below. Real environment variables still win --
# load_dotenv does not override what is already set.
from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(_BACKEND_DIR / ".env")            # backend/.env  (preferred)
load_dotenv(_BACKEND_DIR.parent / ".env")     # repo-root .env (fallback)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.app.voice.tts import speak
from backend.app.plugins.alarm import get_scheduled_alarms
from backend.app.plugins import hardware
import os
import subprocess
import uuid
import whisper
from backend.app.voice.pipeline import VoicePipeline, PipelineConfig

def _build_commit() -> str:
    """Short git SHA of the running checkout, for /health.

    Best-effort: a deploy without git, or without a .git directory, degrades to
    "unknown" rather than breaking the route.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_BACKEND_DIR.parent),
            capture_output=True, text=True, timeout=3,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


BUILD_COMMIT = _build_commit()

app = FastAPI(
    title="ISIRI 2.0 Backend",
    description="Intelligent Speech Interface for Regional Interaction",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Load Whisper model once at startup
model = whisper.load_model("base")

# Initialize VoicePipeline once at startup
pipeline_config = PipelineConfig(
    wake_word_enabled=False,
    vad_enabled=False,
    translation_enabled=True,
    language="en",
    hardware_integration=False
)
pipeline = VoicePipeline(pipeline_config)
pipeline.initialize()

@app.get("/alarms")
async def list_alarms():
    return {"scheduled_alarms": get_scheduled_alarms()}


@app.get("/health")
def health():
    """Answers 'is the process on this port actually running my code?'

    A stale uvicorn still bound to the port is the classic cause of the lock
    routes 404-ing, and it is otherwise invisible. Compare `commit` here with
    `git log --oneline -1` on disk.
    """
    lock_routes = sorted(
        {route.path for route in app.routes
         if getattr(route, "path", "").startswith("/device/lock")}
    )

    raw_host = os.environ.get("RPI_HOST", "")
    try:
        parsed = list(hardware.parse_rpi_host(raw_host))
        parse_error = None
    except ValueError as error:
        parsed, parse_error = None, str(error)

    status = hardware.get_status()

    return {
        "commit": BUILD_COMMIT,
        "rpi_host": raw_host,
        "parsed": parsed,
        "parse_error": parse_error,
        "lock_routes": lock_routes,
        "pi_reachable": bool(status.get("rpi_connected")),
        "lock_state": status.get("state"),
    }


@app.get("/device/lock/diag")
def lock_diagnostics():
    """Run this first when the lock 'doesn't work' on a new machine.

    Reports the raw RPI_HOST, how it parsed, what it resolved to (including the
    IPv6 scope_id), and whether the Pi answered -- so a config typo can be told
    apart from a firewall problem without involving the microphone.
    """
    return hardware.diagnostics()


@app.get("/device/lock/status")
def lock_status():
    return hardware.get_status()


@app.post("/device/lock/{state}")
def lock_set(state: str):
    """Drive the lock without speaking: curl -X POST .../device/lock/locked"""
    return hardware.execute({"state": state})


@app.get("/")
async def root():
    """
    Root endpoint returning a welcome message.
    """
    return {"message": "Welcome to ISIRI 2.0 Backend"}


@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):
    print("UPLOAD ENDPOINT CALLED")

    file_extension = audio.filename.split(".")[-1] if "." in audio.filename else "webm"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(await audio.read())

    print("Audio saved:", file_path)

    try:
        print("Starting Whisper...")
        result = model.transcribe(
            str(file_path),
            language="en",
            fp16=False,
            temperature=0.0,
            condition_on_previous_text=False,
            initial_prompt=(
                "Baakil lock malpule. Baakil unlock malpule. Youtube open malpule. "
                "Yencha ullar? Spotify open malpule. Weather in Mangalore. "
                "Set an alarm for seven am."
            ),
        )
        print("Whisper finished!")
        print(result)

        transcription = result["text"]
        
        # Process transcription through VoicePipeline
        ai_result = pipeline.process_with_ai(transcription)
        
        print("AI Result:", ai_result)

    except Exception as e:
        print("ERROR:", e)
        return {
            "success": False,
            "error": str(e)
        }

    import asyncio

    if ai_result.get("response"):
        asyncio.create_task(
            speak(ai_result["response"])
        )

    return {
        "success": True,
        "transcription": transcription,
        "intent": ai_result["intent"],
        "entities": ai_result["entities"],
        "reply": ai_result["response"],
        "link": ai_result.get("link", ""),
        "weather": ai_result.get("weather"),
        # Hardware/lock outcome. The frontend ignores unknown fields, but these
        # show up in the browser's Network tab, which is how you tell a real
        # servo movement from a simulated one.
        "device": ai_result.get("device"),
        "state": ai_result.get("state"),
        "rpi_connected": ai_result.get("rpi_connected"),
    }


# --- startup banner -------------------------------------------------------
# Printed once at import, i.e. in the uvicorn console. Makes it immediately
# obvious which build booted and where it will look for the Pi.
print("=" * 62)
print("ISIRI 2.0 backend  |  build %s" % BUILD_COMMIT)
print("RPI_HOST           |  %s" % (os.environ.get("RPI_HOST") or "(unset)"))
print("simulation         |  %s" % os.environ.get("HARDWARE_SIMULATION", "false"))
for _route in sorted({r.path for r in app.routes
                      if getattr(r, "path", "").startswith("/device/lock")}):
    print("lock route         |  %s" % _route)
print("=" * 62)
