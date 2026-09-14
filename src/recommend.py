from pathlib import Path
import ast

import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"


# ============================================================
# LOAD RECOMMENDATION DATASETS
# ============================================================

print("Loading recommendation datasets...")

description_df = pd.read_csv(
    RAW_DIR / "description.csv"
)

medications_df = pd.read_csv(
    RAW_DIR / "medications.csv"
)

precautions_df = pd.read_csv(
    RAW_DIR / "precautions.csv"
)

diets_df = pd.read_csv(
    RAW_DIR / "diets.csv"
)

workout_df = pd.read_csv(
    RAW_DIR / "workout.csv"
)

print("Recommendation datasets loaded successfully!")


# ============================================================
# NORMALIZE DISEASE NAME
# ============================================================

def normalize_disease_name(disease):

    disease = str(disease).strip().lower()

    # Handle COPD naming mismatch
    if disease == "copd":
        return "chronic obstructive pulmonary disease (copd)"

    return disease


# ============================================================
# PREPARE LOOKUP TABLES
# ============================================================

description_df["disease_key"] = (
    description_df["Disease"]
    .apply(normalize_disease_name)
)

medications_df["disease_key"] = (
    medications_df["Disease"]
    .apply(normalize_disease_name)
)

precautions_df["disease_key"] = (
    precautions_df["Disease"]
    .apply(normalize_disease_name)
)

diets_df["disease_key"] = (
    diets_df["Disease"]
    .apply(normalize_disease_name)
)

workout_df["disease_key"] = (
    workout_df["Disease"]
    .apply(normalize_disease_name)
)


# ============================================================
# CONVERT STRING LIST INTO PYTHON LIST
# ============================================================

def parse_list(value):

    if pd.isna(value):
        return []

    # If CSV contains a string representation of a list
    if isinstance(value, str):

        try:

            parsed = ast.literal_eval(value)

            if isinstance(parsed, list):

                return [
                    str(item).strip()
                    for item in parsed
                    if str(item).strip()
                ]

        except (ValueError, SyntaxError):
            pass

        # If it is normal text
        return [value.strip()] if value.strip() else []

    return [str(value).strip()] if str(value).strip() else []


# ============================================================
# GET RECOMMENDATIONS
# ============================================================

def get_recommendations(disease):

    disease_key = normalize_disease_name(disease)

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description_result = description_df[
        description_df["disease_key"] == disease_key
    ]

    if description_result.empty:

        description = "Description not available."

    else:

        description = str(
            description_result.iloc[0]["Description"]
        )


    # --------------------------------------------------------
    # MEDICATIONS
    # --------------------------------------------------------

    medication_result = medications_df[
        medications_df["disease_key"] == disease_key
    ]

    if medication_result.empty:

        medications = []

    else:

        medications = parse_list(
            medication_result.iloc[0]["Medication"]
        )


    # --------------------------------------------------------
    # PRECAUTIONS
    # --------------------------------------------------------

    precaution_result = precautions_df[
        precautions_df["disease_key"] == disease_key
    ]

    if precaution_result.empty:

        precautions = []

    else:

        row = precaution_result.iloc[0]

        precautions = []

        for column in [
            "Precaution_1",
            "Precaution_2",
            "Precaution_3",
            "Precaution_4"
        ]:

            if pd.notna(row[column]):

                precaution = str(
                    row[column]
                ).strip()

                if precaution:
                    precautions.append(precaution)


    # --------------------------------------------------------
    # DIET
    # --------------------------------------------------------

    diet_result = diets_df[
        diets_df["disease_key"] == disease_key
    ]

    if diet_result.empty:

        diet = []

    else:

        diet = parse_list(
            diet_result.iloc[0]["Diet"]
        )


    # --------------------------------------------------------
    # WORKOUT
    # --------------------------------------------------------

    workout_result = workout_df[
        workout_df["disease_key"] == disease_key
    ]

    if workout_result.empty:

        workout = []

    else:

        workout = parse_list(
            workout_result.iloc[0]["Workouts"]
        )


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "disease": disease,
        "description": description,
        "medications": medications,
        "precautions": precautions,
        "diet": diet,
        "workout": workout
    }


# ============================================================
# DISPLAY LIST
# ============================================================

def display_list(items):

    if not items:

        print("Information not available.")

        return

    for item in items:

        print(f"• {item}")


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("AI HEALTHMATE RECOMMENDATION SYSTEM")
    print("=" * 70)

    disease = input(
        "\nEnter disease name: "
    ).strip()

    recommendations = get_recommendations(
        disease
    )

    if recommendations["description"] == "Description not available.":

        print(
            "\nDisease not found in the recommendation datasets."
        )

    else:

        print("\n" + "-" * 70)
        print("DESCRIPTION")
        print("-" * 70)

        print(
            recommendations["description"]
        )


        print("\n" + "-" * 70)
        print("MEDICATION INFORMATION")
        print("-" * 70)

        print(
            "The following information is provided for "
            "educational purposes only and is not a prescription. "
            "Consult a qualified healthcare professional before "
            "taking any medication."
        )

        display_list(
            recommendations["medications"]
        )


        print("\n" + "-" * 70)
        print("PRECAUTIONS")
        print("-" * 70)

        display_list(
            recommendations["precautions"]
        )


        print("\n" + "-" * 70)
        print("DIET")
        print("-" * 70)

        display_list(
            recommendations["diet"]
        )


        print("\n" + "-" * 70)
        print("WORKOUT")
        print("-" * 70)

        display_list(
            recommendations["workout"]
        )


        print("\n" + "=" * 70)
        print(
            "DISCLAIMER: AI HealthMate provides educational "
            "information and decision-support only."
        )

        print(
            "The information provided is not a medical diagnosis "
            "or a substitute for professional medical advice."
        )

        print("=" * 70)