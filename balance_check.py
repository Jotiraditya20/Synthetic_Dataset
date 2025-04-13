from collections import Counter
from pathlib import Path
# Synthetic data
synth_labels = [line.split()[0] for f in Path("atraining/train/labels").glob("*.txt") for line in open(f)]
print("Synthetic:", Counter(synth_labels))  # Should be ~33% per class

# Real data
real_labels = [line.split()[0] for f in Path("atraining/valid/labels").glob("*.txt") for line in open(f)]
print("Real:", Counter(real_labels))