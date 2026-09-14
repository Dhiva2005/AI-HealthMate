from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD PROCESSED DATA
# ============================================================

print("Loading processed datasets...")

X_train = pd.read_csv(PROCESSED_DIR / "X_train.csv")
X_test = pd.read_csv(PROCESSED_DIR / "X_test.csv")

y_train = pd.read_csv(PROCESSED_DIR / "y_train.csv")["diseases"]
y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv")["diseases"]

print(f"Training data: {X_train.shape}")
print(f"Testing data: {X_test.shape}")


# ============================================================
# CREATE RANDOM FOREST MODEL
# ============================================================

print("\nCreating Random Forest model...")

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)


# ============================================================
# TRAIN MODEL
# ============================================================

print("Training model...")

model.fit(X_train, y_train)

print("Training completed!")


# ============================================================
# MAKE PREDICTIONS
# ============================================================

print("\nMaking predictions on test data...")

y_pred = model.predict(X_test)


# ============================================================
# EVALUATE MODEL
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

print(f"\nAccuracy: {accuracy:.4f}")
print(f"Accuracy percentage: {accuracy * 100:.2f}%")


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

model_path = MODEL_DIR / "random_forest_model.pkl"

joblib.dump(model, model_path)

print("\n" + "=" * 70)
print("MODEL SAVED")
print("=" * 70)

print(f"\nModel location: {model_path}")