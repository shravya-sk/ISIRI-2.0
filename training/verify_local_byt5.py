import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

path = BASE_DIR / "datasets" / "models" / "byt5_tulu_english"
print(f"Loading ByT5 model from {path}...")
tokenizer = AutoTokenizer.from_pretrained(str(path))
model = AutoModelForSeq2SeqLM.from_pretrained(str(path))
model.eval()

def generate_translation(text, direction="tulu_to_en"):
    prefix = "translate Tulu to English: " if direction == "tulu_to_en" else "translate English to Tulu: "
    prompt = prefix + text
    inputs = tokenizer(prompt, return_tensors="pt", max_length=128, truncation=True)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=40,
            num_beams=3,
            repetition_penalty=1.5,
            no_repeat_ngram_size=2,
            early_stopping=True,
            decoder_start_token_id=0,
            eos_token_id=1,
            pad_token_id=0
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

samples = [
    ("youtube open malpule", "tulu_to_en"),
    ("ini mangalore da weather encha undu", "tulu_to_en"),
    ("yaan illag povond ulle", "tulu_to_en"),
    ("Turn on the bedroom light", "en_to_tulu"),
    ("Open YouTube", "en_to_tulu"),
    ("How are you?", "en_to_tulu")
]

print("\n=== GENERATION TEST RESULTS ===")
for text, d in samples:
    res = generate_translation(text, d)
    print(f"[{d}]\n  Input:  {text}\n  Output: {res}\n")
