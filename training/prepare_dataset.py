import pandas as pd
from pathlib import Path

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "datasets" / "raw" / "tulu_parallel_corpus.xlsx"
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Reading dataset...")

# Read Excel file
df = pd.read_excel(RAW_DATA)

print("\nDataset Loaded Successfully!")
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

print("\nFirst 5 Rows:")
print(df.head())

# Remove empty rows
df = df.dropna()

# Remove duplicate rows
df = df.drop_duplicates()

# Trim spaces
df = df.apply(lambda col: col.astype(str).str.strip())

# Save cleaned dataset
output_file = PROCESSED_DIR / "clean_dataset.csv"

df.to_csv(output_file, index=False, encoding="utf-8")

print("\nClean dataset saved to:")
print(output_file)

print("\nDone!")