import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from ai_engine.engine import AIEngine
from ai_engine.translator import translate_to_english

engine = AIEngine()
engine.initialize()

test_queries = [
    "youtube open malpule",
    "ini Kudla da weather encha undu",
    "Open Notepad",
    "light on malpule",
    "kone da fan off malpule",
    "Yelle baiyag Kudla du barsa barpunda panle dayepandha yaan ooru g povodu",
    "how are you",
    "calculator open malpule"
]

print("\n=== ISIRI 2.0 END-TO-END PIPELINE & HARDWARE TEST ===\n")
for q in test_queries:
    translated = translate_to_english(q)
    res = engine.process(translated)
    print(f"[Input]:      '{q}'")
    print(f"[Translated]: '{translated}'")
    print(f"[Intent]:     {res['intent']}")
    print(f"[Entities]:   {res['entities']}")
    print(f"[Reply]:      {res['response']}")
    print("-" * 60)
