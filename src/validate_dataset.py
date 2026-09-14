from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
RESULTS_DIR = ROOT / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD MAIN DATASET
# ============================================================

print("Loading main dataset...")

main_df = pd.read_csv(
    RAW_DIR / "Diseases_and_Symptoms_dataset.csv"
)

print(f"Main dataset shape: {main_df.shape}")


# ============================================================
# CHECK SYMPTOM VALUES
# ============================================================

print("\n" + "=" * 70)
print("1. CHECKING SYMPTOM VALUES")
print("=" * 70)

symptom_columns = [
    column for column in main_df.columns
    if column != "diseases"
]

invalid_values = {}

for column in symptom_columns:

    values = set(main_df[column].dropna().unique())

    invalid = values - {0, 1}

    if invalid:
        invalid_values[column] = sorted(invalid)


if invalid_values:

    print("\nInvalid values found:")

    for column, values in invalid_values.items():
        print(f"{column}: {values}")

else:

    print("\nAll 230 symptom columns contain only 0 and 1.")


# ============================================================
# CHECK CONSTANT FEATURES
# ============================================================

print("\n" + "=" * 70)
print("2. CHECKING CONSTANT FEATURES")
print("=" * 70)

constant_features = []

for column in symptom_columns:

    if main_df[column].nunique() <= 1:
        constant_features.append(column)


if constant_features:

    print("\nConstant features found:")

    for column in constant_features:
        print(column)

else:

    print("\nNo constant symptom features found.")


# ============================================================
# CHECK DISEASE NAMES
# ============================================================

print("\n" + "=" * 70)
print("3. CHECKING DISEASE NAMES")
print("=" * 70)

main_diseases = set(
    main_df["diseases"]
    .astype(str)
    .str.strip()
    .str.lower()
    .unique()
)

print(f"\nDiseases in main dataset: {len(main_diseases)}")


# ============================================================
# LOAD RECOMMENDATION DATASETS
# ============================================================

recommendation_files = {
    "description.csv": "Description",
    "medications.csv": "Medication",
    "precautions.csv": "Precautions",
    "diets.csv": "Diet",
    "workout.csv": "Workouts"
}


recommendation_diseases = {}


for filename in recommendation_files:

    df = pd.read_csv(RAW_DIR / filename)

    diseases = set(
        df["Disease"]
        .astype(str)
        .str.strip()
        .str.lower()
        .unique()
    )

    recommendation_diseases[filename] = diseases

    print(
        f"{filename}: {len(diseases)} diseases"
    )


# ============================================================
# COMPARE DISEASE NAMES
# ============================================================

print("\n" + "=" * 70)
print("4. CHECKING DISEASE COVERAGE")
print("=" * 70)


coverage_results = []


for filename, diseases in recommendation_diseases.items():

    missing = main_diseases - diseases
    extra = diseases - main_diseases

    coverage_results.append({
        "dataset": filename,
        "main_dataset_diseases": len(main_diseases),
        "recommendation_diseases": len(diseases),
        "missing_diseases": len(missing),
        "extra_diseases": len(extra)
    })

    print(f"\n{filename}")

    if missing:
        print("Missing from recommendation dataset:")

        for disease in sorted(missing):
            print(f"  - {disease}")

    else:
        print("All main diseases are present.")

    if extra:
        print("Extra diseases:")

        for disease in sorted(extra):
            print(f"  - {disease}")

    else:
        print("No extra diseases found.")


# ============================================================
# CHECK DUPLICATE DISEASE ENTRIES
# ============================================================

print("\n" + "=" * 70)
print("5. CHECKING RECOMMENDATION DUPLICATES")
print("=" * 70)


for filename in recommendation_files:

    df = pd.read_csv(RAW_DIR / filename)

    duplicate_diseases = df["Disease"].duplicated().sum()

    print(
        f"{filename}: {duplicate_diseases} duplicate disease entries"
    )


# ============================================================
# SAVE VALIDATION SUMMARY
# ============================================================

coverage_df = pd.DataFrame(coverage_results)

coverage_df.to_csv(
    RESULTS_DIR / "dataset_validation.csv",
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DATASET VALIDATION COMPLETED")
print("=" * 70)

print("\nValidation summary saved to:")

print(
    RESULTS_DIR / "dataset_validation.csv"
)