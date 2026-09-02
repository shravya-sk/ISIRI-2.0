import json
import logging
import os
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import pandas as pd

logger = logging.getLogger(__name__)

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

BYT5_MODEL_PATH = (
    BASE_DIR
    / "datasets"
    / "models"
    / "byt5_tulu_english"
)

# Global lazy references for ByT5 model & tokenizer
_BYT5_TOKENIZER = None
_BYT5_MODEL = None
_BYT5_FAILED = False


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
    if not DATASET_PATH.exists():
        return {}, {}

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
    "google open malpule": "Open Google",
    "google chrome open malpule": "Open Chrome",
    "calculator open malpule": "Open Calculator",
    "notepad open malpule": "Open Notepad",
    "light on malpule": "Turn on the light",
    "light off malpule": "Turn off the light",
    "fan on malpule": "Turn on the fan",
    "fan off malpule": "Turn off the fan",
}

DICTIONARY = load_dictionary()


def get_byt5_pipeline():
    """
    Lazily loads the fine-tuned ByT5-Small model and tokenizer if available.
    Returns (tokenizer, model) or (None, None) if not present or failed.
    """
    global _BYT5_TOKENIZER, _BYT5_MODEL, _BYT5_FAILED

    if _BYT5_FAILED:
        return None, None

    if _BYT5_TOKENIZER is not None and _BYT5_MODEL is not None:
        return _BYT5_TOKENIZER, _BYT5_MODEL

    if not BYT5_MODEL_PATH.exists() or not any(BYT5_MODEL_PATH.iterdir()):
        return None, None

    try:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        logger.info(f"Loading ByT5 neural translation model from: {BYT5_MODEL_PATH}")
        _BYT5_TOKENIZER = AutoTokenizer.from_pretrained(str(BYT5_MODEL_PATH))
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _BYT5_MODEL = AutoModelForSeq2SeqLM.from_pretrained(
            str(BYT5_MODEL_PATH)
        ).to(device)
        _BYT5_MODEL.eval()
        logger.info("ByT5 neural translator loaded successfully.")
        return _BYT5_TOKENIZER, _BYT5_MODEL
    except Exception as e:
        logger.warning(f"Failed to load ByT5 model: {e}. Falling back to rule/retrieval.")
        _BYT5_FAILED = True
        return None, None


def neural_translate(text: str, direction: str = "tulu_to_en") -> Optional[str]:
    """
    Translates text using ByT5-Small Seq2Seq model.
    Returns None if neural model is unavailable or encounters an error.
    """
    tokenizer, model = get_byt5_pipeline()
    if tokenizer is None or model is None:
        return None

    try:
        import torch

        prefix = "translate Tulu to English: " if direction == "tulu_to_en" else "translate English to Tulu: "
        prompt = prefix + text
        inputs = tokenizer(
            prompt, return_tensors="pt", max_length=128, truncation=True
        ).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=48,
                num_beams=3,
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
                early_stopping=True,
                decoder_start_token_id=0,
                eos_token_id=1,
                pad_token_id=0
            )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        # Clean prefix artifacts if present
        for noise in ["translate Tulu to English:", "translate English to Tulu:", "Tulu to English:", "English to Tulu:"]:
            if decoded.lower().startswith(noise.lower()):
                decoded = decoded[len(noise):].strip()

        return decoded if decoded else None
    except Exception as e:
        logger.warning(f"Neural translation error: {e}")
        return None


def translate_to_english(sentence: str) -> str:
    """
    Converts a spoken Tulu/Tulu-English command into canonical English
    before ISIRI detects the intent.
    
    Order of operations:
    1. Instant Alias Match (common voice commands)
    2. Direct English voice command check (no translation needed)
    3. Exact Corpus Lookup (2,825 pairs)
    4. Fuzzy Similarity Retrieval (>= 0.90 threshold)
    5. ByT5 Neural Translation
    6. Dictionary Word-Level Fallback
    """
    sentence = str(sentence).strip()
    sentence_key = normalize(sentence)

    if not sentence_key:
        return sentence

    # 1. Alias lookup
    if sentence_key in COMMAND_ALIASES:
        return COMMAND_ALIASES[sentence_key]

    # 2. English voice command: keep it unchanged if already English
    if sentence_key in ENGLISH_TO_TULU:
        return sentence

    # 3. Exact Tulu command from dataset
    if sentence_key in TULU_TO_ENGLISH:
        return TULU_TO_ENGLISH[sentence_key]

    # 4. Similar Tulu command from dataset
    best_tulu = ""
    best_score = 0.0

    for tulu_sentence in TULU_TO_ENGLISH:
        score = similarity(sentence_key, tulu_sentence)
        if score > best_score:
            best_score = score
            best_tulu = tulu_sentence

    # High threshold prevents incorrect command changes
    if best_score >= 0.90:
        return TULU_TO_ENGLISH[best_tulu]

    # 5. Try ByT5 neural translation if available
    neural_res = neural_translate(sentence, direction="tulu_to_en")
    if neural_res and len(neural_res) > 2:
        return neural_res

    # 6. Final word-level fallback
    translated_words = [
        DICTIONARY.get(word, word)
        for word in sentence.lower().split()
    ]

    return " ".join(translated_words)


def translate_to_tulu(sentence: str) -> str:
    """
    Converts an English sentence to Romanised Tulu for display/TTS.
    """
    sentence = str(sentence).strip()
    sentence_key = normalize(sentence)

    # 1. Exact corpus lookup
    if sentence_key in ENGLISH_TO_TULU:
        return ENGLISH_TO_TULU[sentence_key]

    # 2. Try ByT5 neural translation
    neural_res = neural_translate(sentence, direction="en_to_tulu")
    if neural_res and len(neural_res) > 2:
        return neural_res

    return sentence


def translate(sentence: str) -> str:
    """
    Backward-compatible default:
    translate spoken Tulu command to English.
    """
    return translate_to_english(sentence)