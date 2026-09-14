from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT / "data" / "processed"
MODEL_PATH = ROOT / "models" / "random_forest_model.pkl"

RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading test data...")

X_test = pd.read_csv(PROCESSED_DIR / "X_test.csv")
y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv")["diseases"]

print(f"Test data: {X_test.shape}")


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading trained model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")


# ============================================================
# PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

y_pred = model.predict(X_test)

print("Predictions generated!")


# ============================================================
# BASIC METRICS
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro"
)

weighted_f1 = f1_score(
    y_test,
    y_pred,
    average="weighted"
)


print("\n" + "=" * 70)
print("MODEL PERFORMANCE")
print("=" * 70)

print(f"\nAccuracy:       {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"Macro F1-score: {macro_f1:.4f}")
print(f"Weighted F1:    {weighted_f1:.4f}")


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

report = classification_report(
    y_test,
    y_pred,
    output_dict=True,
    zero_division=0
)

report_df = pd.DataFrame(report).transpose()

print(report_df)


# Save classification report
report_df.to_csv(
    RESULTS_DIR / "classification_report.csv"
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\nGenerating confusion matrix...")

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(20, 18))

sns.heatmap(
    cm,
    cmap="Blues",
    xticklabels=False,
    yticklabels=False
)

plt.title("AI HealthMate - Random Forest Confusion Matrix")
plt.xlabel("Predicted Disease")
plt.ylabel("Actual Disease")

plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "confusion_matrix.png",
    dpi=300
)

plt.close()

print("Confusion matrix saved!")


# ============================================================
# TOP INCORRECT PREDICTIONS
# ============================================================

print("\nFinding most common incorrect predictions...")

comparison = pd.DataFrame({
    "actual": y_test,
    "predicted": y_pred
})

incorrect = comparison[
    comparison["actual"] != comparison["predicted"]
]

error_pairs = (
    incorrect
    .groupby(["actual", "predicted"])
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)

print("\nTop 20 incorrect prediction pairs:")

print(error_pairs.head(20).to_string(index=False))


error_pairs.head(20).to_csv(
    RESULTS_DIR / "top_prediction_errors.csv",
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("EVALUATION COMPLETED")
print("=" * 70)

print("\nGenerated files:")

print("1. results/classification_report.csv")
print("2. results/confusion_matrix.png")
print("3. results/top_prediction_errors.csv")