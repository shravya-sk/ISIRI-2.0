from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from backend.app.voice.tts import speak
import uuid
import whisper
from backend.app.voice.pipeline import VoicePipeline, PipelineConfig

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
        "weather": ai_result.get("weather")
    }
