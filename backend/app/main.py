from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.intent import detect_intent
from app.planner import execute
import uuid
import whisper

app = FastAPI(
    title="ISIRI 2.0 Backend",
    description="Intelligent Speech Interface for Regional Interaction",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Load Whisper model once at startup
model = whisper.load_model("base")


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
        result = model.transcribe(str(file_path))
        print("Whisper finished!")
        print(result)

        transcription = result["text"]
        intent_data = detect_intent(transcription)
        plugin_response = execute(
    intent_data["intent"],
    intent_data["entities"]
)

print("Plugin Response:", plugin_response)

    except Exception as e:
        print("WHISPER ERROR:", e)
        return {
            "success": False,
            "error": str(e)
        }

    return {
    "success": True,
    "transcription": transcription,
    "intent": intent_data["intent"],
    "entities": intent_data["entities"],
    "reply": plugin_response["reply"]
}
