"""
Interactive ByT5-Small Translation Tester for ISIRI 2.0

Allows testing trained ByT5 weights locally for both:
1. Tulu -> English (Voice command normalization for AI engine)
2. English -> Tulu (Assistant response / query translation)
"""

import sys
from pathlib import Path
import torch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

MODEL_PATH = BASE_DIR / "datasets" / "models" / "byt5_tulu_english"


def test_byt5():
    if not MODEL_PATH.exists() or not any(MODEL_PATH.iterdir()):
        print(f"ByT5 model directory not found at: {MODEL_PATH}")
        print(
            "Please train ByT5 using `training/train_byt5.ipynb` on Google Colab / GPU,"
        )
        print(f"then extract the downloaded weights into: {MODEL_PATH}\n")
        print("Falling back to rule/retrieval translator for now...")
        from ai_engine.translator import translate_to_english, translate_to_tulu

        while True:
            cmd = input("\nEnter phrase (or 'exit'): ").strip()
            if cmd.lower() in {"exit", "quit"}:
                break
            print(f"Retrieval -> English: {translate_to_english(cmd)}")
            print(f"Retrieval -> Tulu:    {translate_to_tulu(cmd)}")
        return

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    print(f"Loading ByT5 model from {MODEL_PATH}...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(MODEL_PATH)).to(device)
    model.eval()
    print(f"ByT5 Model loaded on {device}!\n")

    def run_translation(text: str, direction: str = "tulu_to_en"):
        if direction == "tulu_to_en":
            prompt = f"translate Tulu to English: {text}"
        else:
            prompt = f"translate English to Tulu: {text}"

        inputs = tokenizer(
            prompt, return_tensors="pt", max_length=256, truncation=True
        ).to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs, max_length=256, num_beams=3, early_stopping=True
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    print("=== ByT5 Translation Interactive Console ===")
    print("Mode 1: Tulu -> English")
    print("Mode 2: English -> Tulu")
    print("Type 'exit' to quit.\n")

    mode = input("Select Mode [1: Tulu->En, 2: En->Tulu] (default 1): ").strip()
    direction = "en_to_tulu" if mode == "2" else "tulu_to_en"

    while True:
        prompt_label = "Tulu input" if direction == "tulu_to_en" else "English input"
        sentence = input(f"{prompt_label}: ").strip()
        if sentence.lower() in {"exit", "quit"}:
            break
        if sentence.lower() == "switch":
            direction = "en_to_tulu" if direction == "tulu_to_en" else "tulu_to_en"
            print(f"Switched mode to: {direction}")
            continue

        result = run_translation(sentence, direction)
        print(f"Translated: {result}\n")


if __name__ == "__main__":
    test_byt5()
