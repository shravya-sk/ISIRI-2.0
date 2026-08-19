import pandas as pd
from pathlib import Path

from tokenizer import Tokenizer


BASE_DIR = Path(__file__).resolve().parent.parent

DATASET = BASE_DIR / "datasets" / "processed" / "clean_dataset.csv"

ENGLISH_VOCAB = BASE_DIR / "datasets" / "vocabulary" / "english_vocab.json"
TULU_VOCAB = BASE_DIR / "datasets" / "vocabulary" / "tulu_vocab.json"


class TranslationDataset:

    def __init__(self):

        self.df = pd.read_csv(DATASET)

        self.eng_tokenizer = Tokenizer(ENGLISH_VOCAB)
        self.tulu_tokenizer = Tokenizer(TULU_VOCAB)

    def __len__(self):

        return len(self.df)

    def __getitem__(self, index):

        row = self.df.iloc[index]

        english = row["English"]
        tulu = row["Tulu"]

        english_tokens = self.eng_tokenizer.encode(english)
        tulu_tokens = self.tulu_tokenizer.encode(tulu)

        return english_tokens, tulu_tokens


if __name__ == "__main__":

    dataset = TranslationDataset()

    print("Dataset Size :", len(dataset))

    eng, tulu = dataset[0]

    print("\nFirst Sample")

    print("English Tokens :", eng)

    print("Tulu Tokens    :", tulu)