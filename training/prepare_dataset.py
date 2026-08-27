import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"

LABELED_DATA = RAW_DIR / "English_to_English__tulu_DATASET_labeled.xlsx"
PARALLEL_DATA = RAW_DIR / "tulu_parallel_corpus.xlsx"
OUTPUT_FILE = PROCESSED_DIR / "clean_dataset.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def find_column(columns, possible_names):
    normalized_columns = {
        str(column).strip().lower().replace(" ", "_"): column
        for column in columns
    }

    for name in possible_names:
        if name in normalized_columns:
            return normalized_columns[name]

    return None


def read_translation_pairs(file_path):
    df = pd.read_excel(file_path)

    english_column = find_column(
        df.columns,
        ["english", "english_sentence", "source", "en"],
    )

    tulu_column = find_column(
        df.columns,
        ["english_tulu", "tulu", "tulu_sentence", "target"],
    )

    if not english_column or not tulu_column:
        raise ValueError(
            f"Could not find English and Tulu columns in {file_path.name}. "
            f"Found columns: {list(df.columns)}"
        )

    pairs = df[[english_column, tulu_column]].copy()
    pairs.columns = ["English", "Tulu"]

    return pairs


print("Reading labeled dataset...")
labeled_df = read_translation_pairs(LABELED_DATA)

print("Reading Tulu parallel corpus...")
parallel_df = read_translation_pairs(PARALLEL_DATA)

df = pd.concat([labeled_df, parallel_df], ignore_index=True)

print(f"Total rows before cleaning: {len(df)}")

df = df.dropna(subset=["English", "Tulu"])

df["English"] = df["English"].astype(str).str.strip()
df["Tulu"] = df["Tulu"].astype(str).str.strip()

df = df[
    (df["English"] != "")
    & (df["Tulu"] != "")
]

# Keep one target translation for each English source sentence.
# The labeled dataset is read first, so its translation is preferred.
df["english_key"] = (
    df["English"]
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.replace(r"[^\w\s]", "", regex=True)
    .str.strip()
)

before_deduplication = len(df)

df = df.drop_duplicates(subset=["english_key"], keep="first")
df = df.drop(columns=["english_key"])

print(
    "Rows removed because the English sentence was repeated:",
    before_deduplication - len(df),
)

print(f"Total rows after cleaning: {len(df)}")

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

print("\nClean dataset saved to:")
print(OUTPUT_FILE)

print("\nFirst five rows:")
print(df.head())