import json
from pathlib import Path


class Tokenizer:

    def __init__(self, vocab_path):

        with open(vocab_path, "r", encoding="utf-8") as f:
            self.word2idx = json.load(f)

        self.idx2word = {
            int(v): k for k, v in self.word2idx.items()
        }

        self.pad = self.word2idx["<PAD>"]
        self.sos = self.word2idx["<SOS>"]
        self.eos = self.word2idx["<EOS>"]
        self.unk = self.word2idx["<UNK>"]

    def encode(self, sentence):

        words = str(sentence).lower().split()

        tokens = [self.sos]

        for word in words:
            tokens.append(
                self.word2idx.get(word, self.unk)
            )

        tokens.append(self.eos)

        return tokens

    def decode(self, tokens):

        words = []

        for token in tokens:

            if token == self.eos:
                break

            if token in (self.pad, self.sos):
                continue

            words.append(
                self.idx2word.get(token, "<UNK>")
            )

        return " ".join(words)


if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent

    vocab = BASE_DIR / "datasets" / "vocabulary" / "english_vocab.json"

    tokenizer = Tokenizer(vocab)

    sentence = "water"

    encoded = tokenizer.encode(sentence)

    decoded = tokenizer.decode(encoded)

    print("Sentence :", sentence)
    print("Encoded  :", encoded)
    print("Decoded  :", decoded)