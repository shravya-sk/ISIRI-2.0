import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
from pathlib import Path
import torch

p = Path("datasets/models/byt5_tulu_english/training_args.bin")
if p.exists():
    args = torch.load(p, map_location="cpu", weights_only=False)
    print("Num Train Epochs:", getattr(args, "num_train_epochs", "N/A"))
    print("Learning Rate:", getattr(args, "learning_rate", "N/A"))
    print("Output Dir:", getattr(args, "output_dir", "N/A"))
    print("Fp16:", getattr(args, "fp16", "N/A"))
    print("Metric for best model:", getattr(args, "metric_for_best_model", "N/A"))
