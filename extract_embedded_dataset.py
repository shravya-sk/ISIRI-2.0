"""
extract_embedded_dataset.py

Safely pulls the USER_DATASET_TEXT block out of training/merge_user_dataset.py
and saves it as its own standalone file with the CORRECT column names
(ENGLISH / ENGLISH_TULU), WITHOUT touching your live clean_dataset.csv or
running any vocabulary rebuild.

Run this from your project root:
    python extract_embedded_dataset.py
"""

import io
import re
import pandas as pd
from pathlib import Path

SCRIPT_PATH = Path("training/merge_user_dataset.py")
OUTPUT_PATH = Path("training/embedded_dataset_extracted.csv")

source = SCRIPT_PATH.read_text(encoding="utf-8")

match = re.search(
    r'USER_DATASET_TEXT\s*=\s*"""(.*?)"""',
    source,
    re.DOTALL,
)

if not match:
    raise RuntimeError("Could not find USER_DATASET_TEXT block in the script.")

raw_text = match.group(1)

df = pd.read_csv(io.StringIO(raw_text))

# Handle either header naming convention
if "English" in df.columns:
    df = df.rename(columns={"English": "ENGLISH", "Tulu": "ENGLISH_TULU"})

df = df.dropna(subset=["ENGLISH", "ENGLISH_TULU"])
df["ENGLISH"] = df["ENGLISH"].astype(str).str.strip()
df["ENGLISH_TULU"] = df["ENGLISH_TULU"].astype(str).str.strip()
df = df[(df["ENGLISH"] != "") & (df["ENGLISH_TULU"] != "")]

df.to_csv(OUTPUT_PATH, index=False)
print(f"Extracted {len(df)} rows to {OUTPUT_PATH}")
print("This file has NOT touched your live clean_dataset.csv.")
print("Next: merge it in with training/merge_candidates.py")