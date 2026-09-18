import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import pandas as pd
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "datasets" / "processed" / "clean_dataset.csv"

DICTIONARY_PATH = BASE_DIR / "datasets" / "tulu_dictionary.json"

BYT5_MODEL_PATH = BASE_DIR / "datasets" / "models" / "byt5_tulu_english"

_BYT5_TOKENIZER = None
_BYT5_MODEL = None
_BYT5_FAILED = False


def normalize(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def similarity(first, second):
    return fuzz.token_sort_ratio(first, second) / 100.0


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
    "baakil lock malpule": "Lock the door",
    "baakil unlock malpule": "Unlock the door",
    "baakil unlockmalpule": "Unlock the door",
    "door lock malpule": "Lock the door",
    "door unlock malpule": "Unlock the door",
    "door open malpule": "Unlock the door",
    "lock the door": "Lock the door",
    "unlock the door": "Unlock the door",
}

ENGLISH_STOPWORDS = {
    "the", "is", "on", "in", "for", "to", "and", "of", "with", "a", "an",
    "are", "was", "were", "this", "that", "it", "be", "have", "has",
    "do", "does", "my", "your", "please", "some", "me",
}


def looks_like_english(text):
    words = set(re.findall(r"[a-z']+", text.lower()))
    return len(words & ENGLISH_STOPWORDS) >= 2


DICTIONARY = load_dictionary()


def get_byt5_pipeline():
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

        logger.info("Loading ByT5 neural translation model from: %s" % BYT5_MODEL_PATH)
        _BYT5_TOKENIZER = AutoTokenizer.from_pretrained(str(BYT5_MODEL_PATH))
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _BYT5_MODEL = AutoModelForSeq2SeqLM.from_pretrained(str(BYT5_MODEL_PATH)).to(device)
        _BYT5_MODEL.eval()
        logger.info("ByT5 neural translator loaded successfully.")
        return _BYT5_TOKENIZER, _BYT5_MODEL
    except Exception as e:
        logger.warning("Failed to load ByT5 model: %s. Falling back to rule/retrieval." % e)
        _BYT5_FAILED = True
        return None, None


def neural_translate(text, direction="tulu_to_en"):
    tokenizer, model = get_byt5_pipeline()
    if tokenizer is None or model is None:
        return None

    try:
        import torch

        prefix = "translate Tulu to English: " if direction == "tulu_to_en" else "translate English to Tulu: "
        prompt = prefix + text
        inputs = tokenizer(prompt, return_tensors="pt", max_length=128, truncation=True).to(model.device)

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
        noise_prefixes = [
            "translate Tulu to English:",
            "translate English to Tulu:",
            "Tulu to English:",
            "English to Tulu:",
        ]
        for noise in noise_prefixes:
            if decoded.lower().startswith(noise.lower()):
                decoded = decoded[len(noise):].strip()

        return decoded if decoded else None
    except Exception as e:
        logger.warning("Neural translation error: %s" % e)
        return None


def translate_to_english(sentence):
    sentence = str(sentence).strip()
    sentence_key = normalize(sentence)

    if not sentence_key:
        return sentence

    if looks_like_english(sentence):
        return sentence

    if sentence_key in COMMAND_ALIASES:
        return COMMAND_ALIASES[sentence_key]

    if sentence_key in ENGLISH_TO_TULU:
        return sentence

    if sentence_key in TULU_TO_ENGLISH:
        return TULU_TO_ENGLISH[sentence_key]

    best_tulu = ""
    best_score = 0.0

    if len(sentence_key.split()) >= 3:
        for tulu_sentence in TULU_TO_ENGLISH:
            score = similarity(sentence_key, tulu_sentence)
            if score > best_score:
                best_score = score
                best_tulu = tulu_sentence

    if best_score >= 0.90:
        return TULU_TO_ENGLISH[best_tulu]

    neural_res = neural_translate(sentence, direction="tulu_to_en")
    if neural_res and len(neural_res) > 2:
        return neural_res

    translated_words = []
    for raw_word in sentence.split():
        stripped = re.sub(r"^[^\w]+|[^\w]+$", "", raw_word.lower())
        translated_words.append(DICTIONARY.get(stripped, raw_word))
    return " ".join(translated_words)


def translate_to_tulu(sentence):
    sentence = str(sentence).strip()
    sentence_key = normalize(sentence)

    if sentence_key in ENGLISH_TO_TULU:
        return ENGLISH_TO_TULU[sentence_key]

    neural_res = neural_translate(sentence, direction="en_to_tulu")
    if neural_res and len(neural_res) > 2:
        return neural_res

    return sentence


def translate(sentence):
    return translate_to_english(sentence)