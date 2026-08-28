import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.translator import translate_to_english


print("Tulu command translator is ready.")
print("Type 'exit' to stop.\n")

while True:
    sentence = input("Tulu command: ").strip()

    if sentence.lower() in {"exit", "quit"}:
        break

    print(
        "English command:",
        translate_to_english(sentence),
        "\n",
    )