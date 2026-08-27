from pathlib import Path

import torch

from config import (
    EMBEDDING_DIM,
    HIDDEN_DIM,
    NUM_LAYERS,
    DROPOUT,
)
from tokenizer import Tokenizer
from seq2seq_model import Encoder, Decoder, Seq2Seq


BASE_DIR = Path(__file__).resolve().parent.parent

ENGLISH_VOCAB = (
    BASE_DIR / "datasets" / "vocabulary" / "english_vocab.json"
)

TULU_VOCAB = (
    BASE_DIR / "datasets" / "vocabulary" / "tulu_vocab.json"
)

MODEL_PATH = (
    BASE_DIR / "datasets" / "models" / "english_to_tulu_seq2seq.pt"
)

MAX_OUTPUT_LENGTH = 30

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def translate(sentence, model, english_tokenizer, tulu_tokenizer):
    source_tokens = english_tokenizer.encode(sentence)

    source = torch.tensor(
        [source_tokens],
        dtype=torch.long,
    ).to(device)

    model.eval()

    with torch.no_grad():
        hidden, cell = model.encoder(source)

        input_token = torch.tensor(
            [tulu_tokenizer.sos],
            dtype=torch.long,
        ).to(device)

        predicted_tokens = []

        for _ in range(MAX_OUTPUT_LENGTH):
            prediction, hidden, cell = model.decoder(
                input_token,
                hidden,
                cell,
            )

            next_token = prediction.argmax(1).item()

            if next_token == tulu_tokenizer.eos:
                break

            predicted_tokens.append(next_token)

            input_token = torch.tensor(
                [next_token],
                dtype=torch.long,
            ).to(device)

    return tulu_tokenizer.decode(predicted_tokens)


def main():
    english_tokenizer = Tokenizer(ENGLISH_VOCAB)
    tulu_tokenizer = Tokenizer(TULU_VOCAB)

    encoder = Encoder(
        input_dim=len(english_tokenizer.word2idx),
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT,
    )

    decoder = Decoder(
        output_dim=len(tulu_tokenizer.word2idx),
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT,
    )

    model = Seq2Seq(encoder, decoder, device).to(device)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
    )

    model.load_state_dict(checkpoint["model_state_dict"])

    print("English-to-Tulu model is ready.")
    print("Type 'exit' to stop.\n")

    while True:
        sentence = input("English: ").strip()

        if sentence.lower() in {"exit", "quit"}:
            break

        if not sentence:
            continue

        translation = translate(
            sentence,
            model,
            english_tokenizer,
            tulu_tokenizer,
        )

        print(f"Tulu: {translation}\n")


if __name__ == "__main__":
    main()