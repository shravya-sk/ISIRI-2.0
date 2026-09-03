import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
            max_new_tokens=64,
            num_beams=3,
            early_stopping=True,
            decoder_start_token_id=0,
            eos_token_id=1,
            pad_token_id=0
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

samples = [
    ("Open YouTube", "en_to_tulu"),
    ("Turn on the bedroom light", "en_to_tulu"),
    ("Turn off the fan", "en_to_tulu"),
    ("How are you?", "en_to_tulu"),
    ("youtube open malpule", "tulu_to_en"),
    ("ini mangalore da weather encha undu", "tulu_to_en"),
    ("yaan illag povond ulle", "tulu_to_en"),
    ("light on malpule", "tulu_to_en"),
    ("kone da fan off malpule", "tulu_to_en"),
]

print("\n=== DIRECT BYT5 NEURAL INFERENCE TEST ===")
for text, d in samples:
    res = generate_translation(text, d)
    print(f"[{d}]\n  Input:  '{text}'\n  Output: '{res}'\n")
