import json
import re
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "clean_dataset.csv"
)

DICTIONARY_PATH = (
    BASE_DIR
    / "datasets"
    / "tulu_dictionary.json"
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


def load_dictionary():
    if not DICTIONARY_PATH.exists():
        return {}

    with open(DICTIONARY_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_translation_data():
    df = pd.read_csv(DATASET_PATH)

    english_to_tulu = {}
    tulu_to_english = {}

    for _, row in df.iterrows():
        english = str(row["English"]).strip()
        tulu = str(row["Tulu"]).strip()

        english_key = normalize(english)
        tulu_key = normalize(tulu)

        if english_key and tulu_key:
            english_to_tulu.setdefault(english_key, tulu)
            tulu_to_english.setdefault(tulu_key, english)

    return english_to_tulu, tulu_to_english


ENGLISH_TO_TULU, TULU_TO_ENGLISH = load_translation_data()
COMMAND_ALIASES = {
    "yencha ullar": "How are you?",
    "yencha uller": "How are you?",
    "yencha ullar?": "How are you?",
    "youtube open malpule": "Open YouTube",
    "youtube open malpu": "Open YouTube",
    "youtube open malpule?": "Open YouTube",
}
DICTIONARY = load_dictionary()


def translate_to_english(sentence):
    """
    Converts a spoken Tulu/Tulu-English command into English
    before ISIRI detects the intent.
    """

    sentence = str(sentence).strip()
    sentence_key = normalize(sentence)

    if not sentence_key:
        return sentence

    if sentence_key in COMMAND_ALIASES:
        return COMMAND_ALIASES[sentence_key]

    # English voice command: keep it unchanged.
    if sentence_key in ENGLISH_TO_TULU:
        return sentence

    # Exact Tulu command from dataset.
    if sentence_key in TULU_TO_ENGLISH:
        return TULU_TO_ENGLISH[sentence_key]

    # Similar Tulu command from dataset.
    best_tulu = ""
    best_score = 0.0

    for tulu_sentence in TULU_TO_ENGLISH:
        score = similarity(sentence_key, tulu_sentence)

        if score > best_score:
            best_score = score
            best_tulu = tulu_sentence

    # High threshold prevents incorrect command changes.
    if best_score >= 0.95:
        return TULU_TO_ENGLISH[best_tulu]

    # Final word-level fallback.
    translated_words = [
        DICTIONARY.get(word, word)
        for word in sentence.lower().split()
    ]

    return " ".join(translated_words)


def translate_to_tulu(sentence):
    """
    Converts an English sentence to Tulu for display/testing.
    """

    sentence = str(sentence).strip()
    sentence_key = normalize(sentence)

    if sentence_key in ENGLISH_TO_TULU:
        return ENGLISH_TO_TULU[sentence_key]

    return sentence


def translate(sentence):
    """
    Backward-compatible default:
    translate spoken Tulu command to English.
    """

    return translate_to_english(sentence)