import json
from pathlib import Path

dictionary_path = Path("datasets/tulu_dictionary.json")

with open(dictionary_path, "r", encoding="utf-8") as f:
    DICTIONARY = json.load(f)


def translate(sentence):

    sentence = sentence.lower()

    words = sentence.split()

    translated = []

    for word in words:
        translated.append(DICTIONARY.get(word, word))

    return " ".join(translated)