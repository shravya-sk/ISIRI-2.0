"""
ISIRI 2.0 — Spoken Tulu Audio Data Collector & Studio

Interactive tool to record and label speech audio from native Tulu speakers.
Produces a structured acoustic dataset for Whisper evaluation and speech fine-tuning.

Audio Specification:
- Format: WAV (16-bit PCM)
- Channels: Mono (1 channel)
- Sample Rate: 16,000 Hz (Standard for Whisper and speech models)

Outputs:
- datasets/audio_dataset/wavs/<filename>.wav
- datasets/audio_dataset/metadata.csv
"""

import datetime
import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import sounddevice as sd
import soundfile as sf

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"
AUDIO_DIR = BASE_DIR / "datasets" / "audio_dataset"
WAVS_DIR = AUDIO_DIR / "wavs"
METADATA_CSV = AUDIO_DIR / "metadata.csv"

# Ensure directories exist
WAVS_DIR.mkdir(parents=True, exist_ok=True)

DATASET_PROMPTS = PROCESSED_DIR / "complex_dataset_1000.csv"
if not DATASET_PROMPTS.exists():
    DATASET_PROMPTS = PROCESSED_DIR / "clean_dataset.csv"

SAMPLE_RATE = 16000


def initialize_metadata_file():
    if not METADATA_CSV.exists():
        columns = [
            "audio_filename",
            "speaker_id",
            "gender",
            "environment",
            "tulu_transcript",
            "english_translation",
            "intent",
            "duration_seconds",
            "timestamp",
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(METADATA_CSV, index=False, encoding="utf-8")


def get_existing_recordings(speaker_id):
    if not METADATA_CSV.exists():
        return set()
    df = pd.read_csv(METADATA_CSV)
    if "speaker_id" in df.columns and "tulu_transcript" in df.columns:
        return set(df[df["speaker_id"] == speaker_id]["tulu_transcript"].dropna())
    return set()


def record_audio(duration_sec=4.0):
    """Records audio from the microphone for the specified duration at 16kHz Mono."""
    print(f"\n🔴 RECORDING ({duration_sec}s)... Speak clearly into microphone!")
    audio = sd.rec(
        int(duration_sec * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("⏹️  Recording finished.")
    return audio


def play_audio(audio):
    """Plays back the recorded audio."""
    print("🔊 Playing back audio...")
    sd.play(audio, samplerate=SAMPLE_RATE)
    sd.wait()


def main():
    initialize_metadata_file()

    print("=" * 65)
    print("      🎙️  ISIRI 2.0 — Spoken Tulu Audio Data Studio")
    print("=" * 65)

    speaker_id = input("\nEnter Speaker ID (e.g., SPK01, SPK02): ").strip().upper()
    if not speaker_id:
        speaker_id = "SPK01"

    gender = input("Speaker Gender [M/F/Other] (default: M): ").strip().upper()
    if gender not in {"M", "F", "OTHER"}:
        gender = "M"

    print("\nSelect Acoustic Environment:")
    print("1. Quiet Room (Low noise, study/bedroom)")
    print("2. Fan Noise (Standard room with ceiling/table fan on)")
    print("3. Classroom / Office Ambient (Background chatter/movement)")
    print("4. Outdoor / Street Noise")
    env_choice = input("Select [1-4] (default: 1): ").strip()
    env_map = {
        "1": "quiet_room",
        "2": "fan_noise",
        "3": "classroom_ambient",
        "4": "outdoor_ambient",
    }
    environment = env_map.get(env_choice, "quiet_room")

    print(f"\nLoading prompts from: {DATASET_PROMPTS.name}")
    df_prompts = pd.read_csv(DATASET_PROMPTS)

    # Optional intent filter
    intents = sorted(df_prompts["Intent"].unique()) if "Intent" in df_prompts.columns else []
    if intents:
        print("\nAvailable Intent Categories:")
        for idx, it in enumerate(intents, 1):
            print(f"  {idx}. {it}")
        print("  0. All Intents")
        intent_sel = input(f"Choose Intent Category [0-{len(intents)}] (default: 0): ").strip()
        if intent_sel.isdigit() and 1 <= int(intent_sel) <= len(intents):
            selected_intent = intents[int(intent_sel) - 1]
            df_prompts = df_prompts[df_prompts["Intent"] == selected_intent]
            print(f"Filtered to: {selected_intent} ({len(df_prompts)} prompts)")

    recorded_texts = get_existing_recordings(speaker_id)
    print(f"\nSpeaker '{speaker_id}' has already recorded {len(recorded_texts)} commands.")

    df_prompts = df_prompts[~df_prompts["Tulu"].isin(recorded_texts)]
    if len(df_prompts) == 0:
        print("🎉 Congratulations! All available prompts have been recorded for this speaker.")
        return

    print(f"\nRemaining prompts for this session: {len(df_prompts)}")
    print("\nControls per prompt:")
    print("  - Press [ENTER] to start recording")
    print("  - After recording: [ENTER]=Save & Next, [R]=Re-record, [P]=Play, [S]=Skip, [Q]=Quit\n")

    session_count = 0

    for idx, row in df_prompts.iterrows():
        tulu_text = str(row["Tulu"]).strip()
        english_text = str(row["English"]).strip()
        intent_name = str(row.get("Intent", "general")).strip()
        complexity = str(row.get("Complexity", "standard")).strip()

        # Dynamic recording duration based on text length
        word_count = len(tulu_text.split())
        duration = min(max(3.0, word_count * 0.45), 7.0)

        while True:
            print("-" * 65)
            print(f"Prompt #{session_count + 1} | Intent: [{intent_name.upper()}] ({complexity})")
            print(f"🗣️  SPEAK IN TULU:  >>> {tulu_text} <<<")
            print(f"📖 Meaning (EN):   {english_text}")
            print(f"⏱️  Duration:       {duration:.1f} seconds")
            print("-" * 65)

            cmd = input("Press [ENTER] when ready to record (or 's' to skip, 'q' to quit): ").strip().lower()
            if cmd == "q":
                print(f"\nSession finished. Total recordings saved this session: {session_count}")
                return
            if cmd == "s":
                print("Skipped.")
                break

            # Record
            audio_data = record_audio(duration_sec=duration)

            # Review options
            action = input("\n[ENTER] to Save & Next | [R] Re-record | [P] Listen Playback | [S] Skip: ").strip().lower()
            while action == "p":
                play_audio(audio_data)
                action = input("\n[ENTER] to Save & Next | [R] Re-record | [P] Listen Playback | [S] Skip: ").strip().lower()

            if action == "r":
                print("Retrying recording...")
                continue
            if action == "s":
                print("Skipped.")
                break

            # Save recording
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{speaker_id}_{environment}_{intent_name}_{session_count+1:04d}_{timestamp_str}.wav"
            file_path = WAVS_DIR / filename

            sf.write(str(file_path), audio_data, SAMPLE_RATE, subtype="PCM_16")

            # Append metadata
            new_row = {
                "audio_filename": filename,
                "speaker_id": speaker_id,
                "gender": gender,
                "environment": environment,
                "tulu_transcript": tulu_text,
                "english_translation": english_text,
                "intent": intent_name,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.datetime.now().isoformat(),
            }

            df_meta = pd.DataFrame([new_row])
            df_meta.to_csv(METADATA_CSV, mode="a", header=False, index=False, encoding="utf-8")

            session_count += 1
            print(f"✅ Saved as: {filename} ({session_count} recorded this session)\n")
            break

    print(f"\n🎉 Session complete! Recorded {session_count} audio files.")
    print(f"All audio files stored in: {WAVS_DIR}")
    print(f"Metadata recorded in:     {METADATA_CSV}")


if __name__ == "__main__":
    main()
