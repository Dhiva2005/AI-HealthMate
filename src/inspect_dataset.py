from pathlib import Path
import pandas as pd


# Project root directory
ROOT = Path(__file__).resolve().parents[1]

# Raw dataset directory
DATA_DIR = ROOT / "data" / "raw"


def inspect_csv(filename):
    path = DATA_DIR / filename

    print("\n" + "=" * 80)
    print(filename)
    print("=" * 80)

    df = pd.read_csv(path)

    print(f"Shape: {df.shape}")

    print("\nColumns:")
    print(df.columns.tolist())

    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    missing = df.isna().sum()
    missing = missing[missing > 0]

    print("\nMissing values:")
    if missing.empty:
        print("None")
    else:
        print(missing)

    return df


# ============================================================
# MAIN DISEASE + SYMPTOM DATASET
# ============================================================

main_df = inspect_csv("Diseases_and_Symptoms_dataset.csv")

target = "diseases"

if target in main_df.columns:

    print("\n" + "=" * 80)
    print("MAIN DATASET ANALYSIS")
    print("=" * 80)

    print(f"\nTarget column: {target}")

    print(f"Unique diseases: {main_df[target].nunique()}")

    print("\nDisease distribution:")
    print(main_df[target].value_counts())

    symptom_columns = [
        column for column in main_df.columns
        if column != target
    ]

    print(f"\nNumber of symptom features: {len(symptom_columns)}")

    print("\nData types:")
    print(main_df.dtypes.value_counts())

    print("\nFirst 5 rows:")
    print(main_df.head())


# ============================================================
# RECOMMENDATION DATASETS
# ============================================================

description_df = inspect_csv("description.csv")
medications_df = inspect_csv("medications.csv")
precautions_df = inspect_csv("precautions.csv")
diets_df = inspect_csv("diets.csv")
workout_df = inspect_csv("workout.csv")


# ============================================================
# RECOMMENDATION DATASET PREVIEW
# ============================================================

print("\n" + "=" * 80)
print("RECOMMENDATION DATASETS PREVIEW")
print("=" * 80)

datasets = {
    "description.csv": description_df,
    "medications.csv": medications_df,
    "precautions.csv": precautions_df,
    "diets.csv": diets_df,
    "workout.csv": workout_df
}

for name, df in datasets.items():

    print(f"\n{name}")
    print("-" * 50)

    print(f"Shape: {df.shape}")
    print("Columns:", df.columns.tolist())
    print("\nFirst 3 rows:")
    print(df.head(3))


print("\n" + "=" * 80)
print("DATASET INSPECTION COMPLETED")
print("=" * 80)