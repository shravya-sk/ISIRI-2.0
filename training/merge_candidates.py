# -*- coding: utf-8 -*-
"""
merge_candidates.py

Merges the validated ISIRI_candidate_sentences_for_validation.xlsx
(after your team fills in ENGLISH_TULU) into datasets/processed/clean_dataset.csv.

Usage:
    python merge_candidates.py \
        --clean_csv path/to/clean_dataset.csv \
        --candidates_xlsx path/to/ISIRI_candidate_sentences_for_validation.xlsx \
        --out path/to/clean_dataset_v2.csv

Behaviour:
- Skips any candidate row where ENGLISH_TULU is still blank (not yet translated).
- Skips rows the team marked "skip"/"unusable"/etc. in the NOTES column.
- Drops exact duplicate ENGLISH sentences already present in clean_dataset.csv,
  keeping the original entry (same rule your prepare_dataset.py already uses).
- Prints a summary so you can see exactly how many new rows were added and how
  many were skipped, and why.
"""

import argparse
import pandas as pd
import sys

SKIP_KEYWORDS = ["skip", "unusable", "remove", "delete", "bad", "wrong", "n/a", "na"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean_csv", required=True, help="Path to existing clean_dataset.csv")
    parser.add_argument("--candidates_xlsx", required=True, help="Path to the validated candidate sheet")
    parser.add_argument("--out", required=True, help="Path to write the merged CSV")
    args = parser.parse_args()

    clean_df = pd.read_csv(args.clean_csv)
    if str(args.candidates_xlsx).lower().endswith(".csv"):
        cand_df = pd.read_csv(args.candidates_xlsx)
    else:
        cand_df = pd.read_excel(args.candidates_xlsx, sheet_name="Candidates")

    required_cols = {"ENGLISH", "ENGLISH_TULU"}
    if not required_cols.issubset(set(clean_df.columns)):
        print(f"ERROR: clean_dataset.csv is missing expected columns: {required_cols - set(clean_df.columns)}")
        sys.exit(1)
    if not required_cols.issubset(set(cand_df.columns)):
        print(f"ERROR: candidate sheet is missing expected columns: {required_cols - set(cand_df.columns)}")
        sys.exit(1)

    total_candidates = len(cand_df)

    # Normalize strings (fillna BEFORE astype(str) - pandas' nullable/string dtypes
    # can leave real NaNs in place after astype(str), which would silently defeat
    # the blank-translation check below)
    cand_df["ENGLISH"] = cand_df["ENGLISH"].fillna("").astype(str).str.strip()
    cand_df["ENGLISH_TULU"] = cand_df["ENGLISH_TULU"].fillna("").astype(str).str.strip()
    if "NOTES" not in cand_df.columns:
        cand_df["NOTES"] = ""
    cand_df["NOTES"] = cand_df["NOTES"].fillna("").astype(str)

    # Drop rows with no translation yet
    not_yet_translated = cand_df["ENGLISH_TULU"].isin(["", "nan", "None"])
    n_not_translated = not_yet_translated.sum()
    cand_df = cand_df[~not_yet_translated]

    # Drop rows flagged as unusable via NOTES
    def is_flagged_skip(note):
        note_l = note.lower()
        return any(kw in note_l for kw in SKIP_KEYWORDS)

    flagged = cand_df["NOTES"].apply(is_flagged_skip)
    n_flagged = flagged.sum()
    cand_df = cand_df[~flagged]

    # Drop duplicates against existing clean_dataset.csv - checking the
    # (ENGLISH, ENGLISH_TULU) PAIR, not ENGLISH alone, so a genuinely
    # different Tulu paraphrase for an already-known English sentence is
    # correctly kept rather than discarded.
    existing_pairs = set(
        zip(
            clean_df["ENGLISH"].astype(str).str.strip().str.lower(),
            clean_df["ENGLISH_TULU"].astype(str).str.strip().str.lower(),
        )
    )
    cand_pairs = list(
        zip(
            cand_df["ENGLISH"].str.lower(),
            cand_df["ENGLISH_TULU"].str.lower(),
        )
    )
    is_dup = pd.Series(cand_pairs, index=cand_df.index).isin(existing_pairs)
    n_dup = is_dup.sum()
    cand_df = cand_df[~is_dup]

    # Keep only columns that exist in clean_dataset.csv (INTENT/ENTITIES if present there too)
    keep_cols = [c for c in ["ENGLISH", "ENGLISH_TULU", "INTENT", "ENTITIES"] if c in clean_df.columns]
    cand_df_final = cand_df[[c for c in keep_cols if c in cand_df.columns]]

    merged = pd.concat([clean_df, cand_df_final], ignore_index=True)
    # Dedup on the (ENGLISH, ENGLISH_TULU) PAIR, not ENGLISH alone -
    # multiple different Tulu paraphrases for the same English sentence
    # are valid, valuable training diversity and must not be collapsed.
    merged = merged.drop_duplicates(subset=["ENGLISH", "ENGLISH_TULU"], keep="first").reset_index(drop=True)

    merged.to_csv(args.out, index=False)

    print("=== Merge summary ===")
    print(f"Candidate sheet rows total:      {total_candidates}")
    print(f"Skipped (no Tulu translation):   {n_not_translated}")
    print(f"Skipped (flagged in NOTES):      {n_flagged}")
    print(f"Skipped (duplicate of existing): {n_dup}")
    print(f"New rows added:                  {len(cand_df_final)}")
    print(f"Original clean_dataset.csv rows: {len(clean_df)}")
    print(f"Final merged dataset rows:       {len(merged)}")
    print(f"Saved to: {args.out}")


if __name__ == "__main__":
    main()