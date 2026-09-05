# -*- coding: utf-8 -*-
"""
test_model_local.py

Quick local sanity-check for the fine-tuned ByT5 model your friend pushed.
Run this from VS Code (or terminal) after activating the venv and installing
transformers/torch/sentencepiece.

Usage:
    python test_model_local.py
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# UPDATE THIS to the actual folder path where the model files live in your repo,
# e.g. "models/byt5_stage_a_final" or wherever your friend put it.
MODEL_PATH = r"C:\Projects\ISIRI-2.0\datasets\models\byt5_tulu_english"

print(f"Loading model from: {MODEL_PATH}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
model.eval()
print("Model loaded successfully.\n")


def translate(text, direction="en2tu", max_len=128):
    prefix = "translate English to Tulu: " if direction == "en2tu" else "translate Tulu to English: "
    inputs = tokenizer(prefix + text, return_tensors="pt", truncation=True, max_length=max_len)
    output_ids = model.generate(
        **inputs,
        max_length=max_len,
        num_beams=4,
        repetition_penalty=1.3,
        no_repeat_ngram_size=3,
        early_stopping=True,
    )
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)


if __name__ == "__main__":
    test_sentences_en = [
        "Open YouTube",
        "What's the weather in Mangalore?",
        "Set an alarm for 7 am tomorrow because I have a train to catch.",
        "Play some Tulu songs on Spotify.",
    ]

    print("=== English -> Tulu ===")
    for s in test_sentences_en:
        result = translate(s, "en2tu")
        print(f"EN: {s}")
        print(f"TU: {result}\n")

    test_sentences_tu = [
        "Youtube open malpule",
        "Yencha ullar?",
    ]

    print("=== Tulu -> English ===")
    for s in test_sentences_tu:
        result = translate(s, "tu2en")
        print(f"TU: {s}")
        print(f"EN: {result}\n")

    # Interactive mode - type your own sentences to test
    print("=== Interactive mode (type 'quit' to exit) ===")
    while True:
        text = input("\nEnglish sentence (or 'quit'): ").strip()
        if text.lower() == "quit":
            break
        print("->", translate(text, "en2tu"))