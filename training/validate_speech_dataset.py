"""
ISIRI 2.0 — Speech Dataset Validation & Split Generator

Validates collected audio recordings in datasets/audio_dataset/
and generates speaker-independent Train/Validation/Test splits for speech benchmarking.

Usage:
    python training/validate_speech_dataset.py
"""

from pathlib import Path
import pandas as pd
import soundfile as sf

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "datasets" / "audio_dataset"
WAVS_DIR = AUDIO_DIR / "wavs"
METADATA_CSV = AUDIO_DIR / "metadata.csv"

TRAIN_SPLIT_CSV = AUDIO_DIR / "train_split.csv"
VAL_SPLIT_CSV = AUDIO_DIR / "val_split.csv"
TEST_SPLIT_CSV = AUDIO_DIR / "test_split.csv"


def validate_dataset():
    if not METADATA_CSV.exists():
        print(f"Metadata file not found at: {METADATA_CSV}")
        print("Please record audio files first using `python training/speech_collector.py`.")
        return

    df = pd.read_csv(METADATA_CSV)
    if len(df) == 0:
        print("Metadata CSV is empty. Please record audio files using `python training/speech_collector.py`.")
        return

    print("=" * 60)
    print("      📊  ISIRI 2.0 — Spoken Tulu Dataset Analytics")
    print("=" * 60)

    # 1. File verification
    missing_files = 0
    total_duration_sec = 0.0
    verified_records = []

    for _, row in df.iterrows():
        fn = row["audio_filename"]
        fp = WAVS_DIR / fn

        if not fp.exists():
            missing_files += 1
            continue

        try:
            info = sf.info(str(fp))
            total_duration_sec += info.duration
            verified_records.append(row)
        except Exception as e:
            print(f"Error reading {fn}: {e}")
            missing_files += 1

    df_valid = pd.DataFrame(verified_records)

    total_hours = total_duration_sec / 3600.0
    total_minutes = total_duration_sec / 60.0

    print(f"\n✅ Total Verified Audio Files:   {len(df_valid)}")
    if missing_files > 0:
        print(f"⚠️  Missing / Corrupt Files:     {missing_files}")
    print(f"⏱️  Total Audio Duration:        {total_minutes:.2f} mins ({total_hours:.2f} hours)")
    print(f"📏 Average Duration per Sample:  {total_duration_sec / max(1, len(df_valid)):.2f} sec")

    # 2. Speaker Breakdown
    print("\n👥 Speaker Distribution:")
    spk_counts = df_valid["speaker_id"].value_counts()
    for spk, count in spk_counts.items():
        gender = df_valid[df_valid["speaker_id"] == spk]["gender"].iloc[0]
        print(f"  - Speaker {spk} ({gender}): {count} recordings")

    # 3. Environment Breakdown
    print("\n🎙️  Acoustic Environment Distribution:")
    env_counts = df_valid["environment"].value_counts()
    for env, count in env_counts.items():
        print(f"  - {env}: {count} recordings ({count / len(df_valid) * 100:.1f}%)")

    # 4. Intent Breakdown
    print("\n🎯 Intent Distribution:")
    intent_counts = df_valid["intent"].value_counts()
    for it, count in intent_counts.items():
        print(f"  - {it}: {count} recordings")

    # 5. Generate Speaker-Independent Train / Val / Test Splits
    unique_speakers = list(df_valid["speaker_id"].unique())
    if len(unique_speakers) >= 3:
        # Speaker independent split
        test_spk = [unique_speakers[-1]]
        val_spk = [unique_speakers[-2]]
        train_spk = unique_speakers[:-2]

        train_df = df_valid[df_valid["speaker_id"].isin(train_spk)]
        val_df = df_valid[df_valid["speaker_id"].isin(val_spk)]
        test_df = df_valid[df_valid["speaker_id"].isin(test_spk)]

        train_df.to_csv(TRAIN_SPLIT_CSV, index=False, encoding="utf-8")
        val_df.to_csv(VAL_SPLIT_CSV, index=False, encoding="utf-8")
        test_df.to_csv(TEST_SPLIT_CSV, index=False, encoding="utf-8")

        print("\n📂 Generated Speaker-Independent Evaluation Splits:")
        print(f"  - Train Set ({train_spk}): {len(train_df)} samples -> {TRAIN_SPLIT_CSV.name}")
        print(f"  - Val Set   ({val_spk}):   {len(val_df)} samples -> {VAL_SPLIT_CSV.name}")
        print(f"  - Test Set  ({test_spk}):  {len(test_df)} samples -> {TEST_SPLIT_CSV.name}")
    else:
        print("\nℹ️  Collect recordings from at least 3 speakers to generate speaker-independent splits.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    validate_dataset()
