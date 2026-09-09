import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
path = BASE_DIR / "datasets" / "models" / "byt5_tulu_english"
tokenizer = AutoTokenizer.from_pretrained(str(path))
model = AutoModelForSeq2SeqLM.from_pretrained(str(path))
model.eval()

df = pd.read_csv(BASE_DIR / "datasets" / "processed" / "clean_dataset.csv")

print("=== CHECKING MODEL LOSS ON TRAINING EXAMPLES ===")
for i in range(5):
    row = df.iloc[i]
    tu = str(row["Tulu"]).strip()
    en = str(row["English"]).strip()
    
    prompt = f"translate Tulu to English: {tu}"
    inputs = tokenizer(prompt, return_tensors="pt")
    labels = tokenizer(en, return_tensors="pt")["input_ids"]
    
    with torch.no_grad():
        out = model(**inputs, labels=labels)
        loss = out.loss.item()
        
        # Test greedy generation
        gen_greedy = model.generate(**inputs, max_new_tokens=40, do_sample=False, num_beams=1)
        pred_greedy = tokenizer.decode(gen_greedy[0], skip_special_tokens=True).strip()
        
        # Test beam search
        gen_beam = model.generate(**inputs, max_new_tokens=40, num_beams=4, early_stopping=True)
        pred_beam = tokenizer.decode(gen_beam[0], skip_special_tokens=True).strip()
        
    print(f"\n[Sample {i+1}]")
    print(f"  Prompt:   '{prompt}'")
    print(f"  Target:   '{en}'")
    print(f"  Loss:     {loss:.4f}")
    print(f"  Greedy:   '{pred_greedy}'")
    print(f"  Beam(4):  '{pred_beam}'")
