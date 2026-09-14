from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "results"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading prediction errors...")

errors = pd.read_csv(
    RESULTS_DIR / "top_prediction_errors.csv"
)

label_mapping = pd.read_csv(
    PROCESSED_DIR / "label_mapping.csv"
)


# ============================================================
# CREATE LABEL MAPPING
# ============================================================

label_map = dict(
    zip(
        label_mapping["encoded_label"],
        label_mapping["disease"]
    )
)


# ============================================================
# CONVERT NUMERIC LABELS TO DISEASE NAMES
# ============================================================

errors["actual_disease"] = errors["actual"].map(label_map)

errors["predicted_disease"] = errors["predicted"].map(label_map)


# ============================================================
# REORDER COLUMNS
# ============================================================

errors = errors[
    [
        "actual",
        "actual_disease",
        "predicted",
        "predicted_disease",
        "count"
    ]
]


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 90)
print("TOP DISEASE PREDICTION ERRORS")
print("=" * 90)

print(
    errors.to_string(index=False)
)


# ============================================================
# SAVE HUMAN-READABLE RESULTS
# ============================================================

output_path = RESULTS_DIR / "human_readable_errors.csv"

errors.to_csv(
    output_path,
    index=False
)


print("\n" + "=" * 90)
print("ERROR ANALYSIS COMPLETED")
print("=" * 90)

print(f"\nSaved to:")
print(output_path)