import random
from pathlib import Path

import torch
import torch.nn as nn
from torch.nn.utils import clip_grad_norm_
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, random_split

from config import (
    EMBEDDING_DIM,
    HIDDEN_DIM,
    NUM_LAYERS,
    DROPOUT,
    BATCH_SIZE,
    LEARNING_RATE,
    EPOCHS,
)
from dataloader import TranslationDataset
from seq2seq_model import Encoder, Decoder, Seq2Seq


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "datasets" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "english_to_tulu_seq2seq.pt"

SEED = 42
torch.manual_seed(SEED)
random.seed(SEED)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def create_collate_function(english_pad_idx, tulu_pad_idx):
    def collate_batch(batch):
        english_batch = [
            torch.tensor(english_tokens, dtype=torch.long)
            for english_tokens, _ in batch
        ]

        tulu_batch = [
            torch.tensor(tulu_tokens, dtype=torch.long)
            for _, tulu_tokens in batch
        ]

        english_batch = pad_sequence(
            english_batch,
            batch_first=True,
            padding_value=english_pad_idx,
        )

        tulu_batch = pad_sequence(
            tulu_batch,
            batch_first=True,
            padding_value=tulu_pad_idx,
        )

        return english_batch, tulu_batch

    return collate_batch


def calculate_loss(model, loader, criterion):
    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for source, target in loader:
            source = source.to(device)
            target = target.to(device)

            output = model(
                source,
                target,
                teacher_forcing_ratio=0.0,
            )

            output = output[:, 1:].reshape(-1, output.shape[-1])
            target = target[:, 1:].reshape(-1)

            loss = criterion(output, target)
            total_loss += loss.item()

    return total_loss / max(len(loader), 1)


def main():
    print(f"Using device: {device}")

    dataset = TranslationDataset()
    total_size = len(dataset)

    train_size = int(total_size * 0.80)
    validation_size = int(total_size * 0.10)
    test_size = total_size - train_size - validation_size

    train_data, validation_data, test_data = random_split(
        dataset,
        [train_size, validation_size, test_size],
        generator=torch.Generator().manual_seed(SEED),
    )

    collate_fn = create_collate_function(
        dataset.eng_tokenizer.pad,
        dataset.tulu_tokenizer.pad,
    )

    train_loader = DataLoader(
        train_data,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=collate_fn,
    )

    validation_loader = DataLoader(
        validation_data,
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collate_fn,
    )

    test_loader = DataLoader(
        test_data,
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collate_fn,
    )

    encoder = Encoder(
        input_dim=len(dataset.eng_tokenizer.word2idx),
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT,
    )

    decoder = Decoder(
        output_dim=len(dataset.tulu_tokenizer.word2idx),
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT,
    )

    model = Seq2Seq(encoder, decoder, device).to(device)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    criterion = nn.CrossEntropyLoss(
        ignore_index=dataset.tulu_tokenizer.pad,
    )

    best_validation_loss = float("inf")

    print(f"Total samples: {total_size}")
    print(f"Train samples: {train_size}")
    print(f"Validation samples: {validation_size}")
    print(f"Test samples: {test_size}")

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_train_loss = 0.0

        for source, target in train_loader:
            source = source.to(device)
            target = target.to(device)

            optimizer.zero_grad()

            output = model(
                source,
                target,
                teacher_forcing_ratio=0.5,
            )

            output = output[:, 1:].reshape(-1, output.shape[-1])
            target = target[:, 1:].reshape(-1)

            loss = criterion(output, target)

            loss.backward()

            clip_grad_norm_(model.parameters(), max_norm=1.0)

            optimizer.step()

            total_train_loss += loss.item()

        average_train_loss = total_train_loss / max(len(train_loader), 1)

        validation_loss = calculate_loss(
            model,
            validation_loader,
            criterion,
        )

        print(
            f"Epoch {epoch}/{EPOCHS} | "
            f"Train Loss: {average_train_loss:.4f} | "
            f"Validation Loss: {validation_loss:.4f}"
        )

        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "english_vocab_size": len(dataset.eng_tokenizer.word2idx),
                    "tulu_vocab_size": len(dataset.tulu_tokenizer.word2idx),
                    "best_validation_loss": best_validation_loss,
                },
                MODEL_PATH,
            )

            print("Best model saved.")

    checkpoint = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])

    test_loss = calculate_loss(
        model,
        test_loader,
        criterion,
    )

    print(f"\nFinal Test Loss: {test_loss:.4f}")
    print(f"Model saved at: {MODEL_PATH}")


if __name__ == "__main__":
    main()