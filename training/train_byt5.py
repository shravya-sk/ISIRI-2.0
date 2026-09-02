"""
ByT5-Small Fine-Tuning for Bidirectional Romanised Tulu <-> English Translation

This script fine-tunes google/byt5-small using Hugging Face's Seq2SeqTrainer.
ByT5 operates at the raw byte level (UTF-8), eliminating out-of-vocabulary (<UNK>)
errors on non-standardised Romanised Tulu spellings.

Usage:
    python training/train_byt5.py --epochs 15 --batch_size 8 --learning_rate 5e-4
"""

import argparse
import os
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from datasets import Dataset, DatasetDict
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    set_seed,
)
import evaluate

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATASET_PATH = BASE_DIR / "datasets" / "processed" / "clean_dataset.csv"
DEFAULT_OUTPUT_DIR = BASE_DIR / "datasets" / "models" / "byt5_tulu_english"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fine-tune ByT5-Small on Tulu <-> English parallel corpus."
    )
    parser.add_argument(
        "--dataset_path",
        type=str,
        default=str(DEFAULT_DATASET_PATH),
        help="Path to clean_dataset.csv",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="google/byt5-small",
        help="Hugging Face model checkpoint",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to save the fine-tuned model",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=15,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=8,
        help="Per-device train/eval batch size",
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=4,
        help="Number of updates steps to accumulate before performing a backward/update pass",
    )
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=5e-4,
        help="Initial learning rate (Adafactor/AdamW)",
    )
    parser.add_argument(
        "--max_source_length",
        type=int,
        default=256,
        help="Max byte sequence length for input text",
    )
    parser.add_argument(
        "--max_target_length",
        type=int,
        default=256,
        help="Max byte sequence length for target text",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    return parser.parse_args()


def load_and_prepare_bidirectional_data(dataset_path: str, seed: int = 42):
    """
    Loads parallel dataset and generates bidirectional training examples:
    - Task 1: "translate Tulu to English: {tulu}" -> "{english}"
    - Task 2: "translate English to Tulu: {english}" -> "{tulu}"
    """
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)

    df = df.dropna(subset=["English", "Tulu"])
    df["English"] = df["English"].astype(str).str.strip()
    df["Tulu"] = df["Tulu"].astype(str).str.strip()
    df = df[(df["English"] != "") & (df["Tulu"] != "")]

    inputs = []
    targets = []
    directions = []

    for _, row in df.iterrows():
        en_text = row["English"]
        tu_text = row["Tulu"]

        # Direction 1: Tulu -> English
        inputs.append(f"translate Tulu to English: {tu_text}")
        targets.append(en_text)
        directions.append("tulu_to_en")

        # Direction 2: English -> Tulu
        inputs.append(f"translate English to Tulu: {en_text}")
        targets.append(tu_text)
        directions.append("en_to_tulu")

    full_dataset = Dataset.from_dict(
        {
            "input_text": inputs,
            "target_text": targets,
            "direction": directions,
        }
    )

    # Train / Val / Test split: 80% / 10% / 10%
    train_test_split = full_dataset.train_test_split(test_size=0.2, seed=seed)
    test_valid_split = train_test_split["test"].train_test_split(
        test_size=0.5, seed=seed
    )

    dataset_dict = DatasetDict(
        {
            "train": train_test_split["train"],
            "validation": test_valid_split["train"],
            "test": test_valid_split["test"],
        }
    )

    print(
        f"Prepared bidirectional pairs -> Train: {len(dataset_dict['train'])}, "
        f"Validation: {len(dataset_dict['validation'])}, Test: {len(dataset_dict['test'])}"
    )
    return dataset_dict


def main():
    args = parse_args()
    set_seed(args.seed)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # 1. Load data
    dataset_dict = load_and_prepare_bidirectional_data(
        args.dataset_path, seed=args.seed
    )

    # 2. Load tokenizer & model
    print(f"Loading tokenizer & model: {args.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)

    # 3. Preprocess function
    def preprocess_function(examples):
        model_inputs = tokenizer(
            examples["input_text"],
            max_length=args.max_source_length,
            truncation=True,
            padding=False,
        )
        labels = tokenizer(
            text_target=examples["target_text"],
            max_length=args.max_target_length,
            truncation=True,
            padding=False,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    print("Tokenizing datasets...")
    tokenized_datasets = dataset_dict.map(
        preprocess_function,
        batched=True,
        remove_columns=["input_text", "target_text", "direction"],
    )

    # 4. Metrics Setup (BLEU + chrF++)
    sacrebleu_metric = evaluate.load("sacrebleu")
    chrf_metric = evaluate.load("chrf")

    def decode_byt5_sequences(sequences):
        decoded = []
        for seq in sequences:
            raw_bytes = bytearray(
                [int(t) - 3 for t in seq if 3 <= int(t) <= 258]
            )
            decoded.append(raw_bytes.decode("utf-8", errors="ignore").strip())
        return decoded

    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]

        decoded_preds = decode_byt5_sequences(preds)
        decoded_labels = [[l] for l in decode_byt5_sequences(labels)]

        bleu_res = sacrebleu_metric.compute(
            predictions=decoded_preds, references=decoded_labels
        )
        chrf_res = chrf_metric.compute(
            predictions=decoded_preds, references=decoded_labels
        )

        return {
            "bleu": round(bleu_res["score"], 2),
            "chrf": round(chrf_res["score"], 2),
        }

    # 5. Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        model=model,
        label_pad_token_id=-100,
        pad_to_multiple_of=8 if device == "cuda" else None,
    )

    # 6. Training Arguments
    use_fp16 = device == "cuda" and torch.cuda.is_available()

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        weight_decay=0.01,
        save_total_limit=2,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        generation_max_length=args.max_target_length,
        generation_num_beams=3,
        fp16=use_fp16,
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="chrf",
        greater_is_better=True,
        report_to="none",
        dataloader_num_workers=2 if os.name != "nt" else 0,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    # 7. Train
    print("\nStarting ByT5 training...")
    trainer.train()

    # 8. Evaluate on test set
    print("\nEvaluating on Test Set...")
    test_results = trainer.predict(
        test_dataset=tokenized_datasets["test"],
        metric_key_prefix="test",
    )
    print(f"Test BLEU: {test_results.metrics.get('test_bleu')}")
    print(f"Test chrF: {test_results.metrics.get('test_chrf')}")

    # 9. Save final model & tokenizer
    print(f"\nSaving best model to {args.output_dir}...")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Model and tokenizer saved successfully!")


if __name__ == "__main__":
    main()
