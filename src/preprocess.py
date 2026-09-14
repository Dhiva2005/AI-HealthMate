from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

RAW_DATA = ROOT / "data" / "raw" / "Diseases_and_Symptoms_dataset.csv"
PROCESSED_DIR = ROOT / "data" / "processed"


# Create processed directory if it does not exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading dataset...")

df = pd.read_csv(RAW_DATA)

print(f"Dataset loaded: {df.shape}")


# ============================================================
# BASIC VALIDATION
# ============================================================

print("\nChecking dataset...")

print(f"Missing values: {df.isna().sum().sum()}")
print(f"Duplicate rows: {df.duplicated().sum()}")


# ============================================================
# SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(columns=["diseases"])
y = df["diseases"]


print(f"\nNumber of features: {X.shape[1]}")
print(f"Number of samples: {X.shape[0]}")
print(f"Number of diseases: {y.nunique()}")


# ============================================================
# ENCODE DISEASE LABELS
# ============================================================

print("\nEncoding disease labels...")

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)


print(f"Number of encoded classes: {len(label_encoder.classes_)}")

print("\nExample label mapping:")

for number, disease in enumerate(label_encoder.classes_[:10]):
    print(f"{number} -> {disease}")


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)


print(f"Training samples: {X_train.shape[0]}")
print(f"Testing samples: {X_test.shape[0]}")


# ============================================================
# SAVE PROCESSED DATA
# ============================================================

print("\nSaving processed datasets...")

X_train.to_csv(PROCESSED_DIR / "X_train.csv", index=False)
X_test.to_csv(PROCESSED_DIR / "X_test.csv", index=False)

pd.Series(y_train, name="diseases").to_csv(
    PROCESSED_DIR / "y_train.csv",
    index=False
)

pd.Series(y_test, name="diseases").to_csv(
    PROCESSED_DIR / "y_test.csv",
    index=False
)

# Save disease label mapping
label_mapping = pd.DataFrame({
    "encoded_label": range(len(label_encoder.classes_)),
    "disease": label_encoder.classes_
})

label_mapping.to_csv(
    PROCESSED_DIR / "label_mapping.csv",
    index=False
)


# ============================================================
# COMPLETED
# ============================================================

print("\n" + "=" * 70)
print("PREPROCESSING COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nGenerated files:")

print("1. X_train.csv")
print("2. X_test.csv")
print("3. y_train.csv")
print("4. y_test.csv")
print("5. label_mapping.csv")