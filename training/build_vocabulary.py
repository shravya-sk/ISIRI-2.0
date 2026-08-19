import pandas as pd
from pathlib import Path
import json

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATASET = BASE_DIR / "datasets" / "processed" / "clean_dataset.csv"
VOCAB_DIR = BASE_DIR / "datasets" / "vocabulary"

VOCAB_DIR.mkdir(parents=True, exist_ok=True)

print("Loading cleaned dataset...")

df = pd.read_csv(DATASET)

# -----------------------------
# Create vocabularies
# -----------------------------

english_words = set()
tulu_words = set()

for sentence in df["English"]:
    english_words.update(str(sentence).lower().split())

for sentence in df["Tulu"]:
    tulu_words.update(str(sentence).split())

# -----------------------------
# Special Tokens
# -----------------------------

SPECIAL_TOKENS = ["<PAD>", "<SOS>", "<EOS>", "<UNK>"]

english_vocab = SPECIAL_TOKENS + sorted(list(english_words))
tulu_vocab = SPECIAL_TOKENS + sorted(list(tulu_words))

# -----------------------------
# Create word → index mapping
# -----------------------------

english_word2idx = {word: idx for idx, word in enumerate(english_vocab)}
tulu_word2idx = {word: idx for idx, word in enumerate(tulu_vocab)}

# -----------------------------
# Save vocabularies
# -----------------------------

with open(VOCAB_DIR / "english_vocab.json", "w", encoding="utf-8") as f:
    json.dump(english_word2idx, f, ensure_ascii=False, indent=4)

with open(VOCAB_DIR / "tulu_vocab.json", "w", encoding="utf-8") as f:
    json.dump(tulu_word2idx, f, ensure_ascii=False, indent=4)

print("\nVocabulary Created Successfully!")
print(f"English Vocabulary Size : {len(english_vocab)}")
print(f"Tulu Vocabulary Size    : {len(tulu_vocab)}")

print("\nSaved to:")
print(VOCAB_DIR)