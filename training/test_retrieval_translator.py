import re
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = (
    BASE_DIR / "datasets" / "processed" / "clean_dataset.csv"
)


def normalize(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def similarity(first, second):
    return SequenceMatcher(
        None,
        first,
        second,
    ).ratio()


def main():
    df = pd.read_csv(DATASET_PATH)

    translations = {}

    for _, row in df.iterrows():
        english = normalize(row["English"])
        tulu = str(row["Tulu"]).strip()

        if english and tulu:
            translations.setdefault(english, tulu)

    print(f"Loaded {len(translations)} unique translations.")
    print("Type 'exit' to stop.\n")

    while True:
        sentence = input("English: ").strip()

        if sentence.lower() in {"exit", "quit"}:
            break

        normalized_sentence = normalize(sentence)

        if normalized_sentence in translations:
            print("Match: exact")
            print(f"Tulu: {translations[normalized_sentence]}\n")
            continue

        best_sentence = ""
        best_score = 0.0

        for english_sentence in translations:
            score = similarity(
                normalized_sentence,
                english_sentence,
            )

            if score > best_score:
                best_score = score
                best_sentence = english_sentence

        if best_score >= 0.70:
            print(f"Match: similar ({best_score:.0%})")
            print(f"Closest English: {best_sentence}")
            print(f"Tulu: {translations[best_sentence]}\n")
        else:
            print(
                "No reliable translation was found in the dataset.\n"
            )


if __name__ == "__main__":
    main()