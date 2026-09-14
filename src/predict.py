from pathlib import Path

import pandas as pd
import joblib


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT / "data" / "processed"
MODEL_PATH = ROOT / "models" / "random_forest_model.pkl"


# ============================================================
# SYMPTOM ALIASES
# ============================================================

SYMPTOM_ALIASES = {
    "head ache": "headache",
    "head pain": "headache",

    "pain in hand": "hand or finger pain",
    "pain in hands": "hand or finger pain",

    "pain in leg": "leg pain",
    "pain in legs": "leg pain",

    "pain in arm": "arm pain",
    "pain in arms": "arm pain",

    "pain in foot": "foot or toe pain",
    "pain in feet": "foot or toe pain",

    "pain in toe": "foot or toe pain",
    "pain in toes": "foot or toe pain",

    "pain in knee": "knee pain",
    "pain in knees": "knee pain",

    "pain in hip": "hip pain",
    "pain in hips": "hip pain",

    "pain in ankle": "ankle pain",
    "pain in ankles": "ankle pain",

    "pain in elbow": "elbow pain",
    "pain in elbows": "elbow pain",

    "shortness of breath": "shortness of breath",
    "breathing difficulty": "difficulty breathing",
    "difficulty breathing": "difficulty breathing",

    "stomach pain": "sharp abdominal pain",
    "abdominal pain": "sharp abdominal pain",

    "throwing up": "vomiting",
    "vomit": "vomiting",

    "loose motion": "diarrhea",
    "loose stools": "diarrhea",

    "high temperature": "fever",

    "tiredness": "fatigue",
    "tired": "fatigue",

    "skin itching": "itching of skin",
    "itching": "itching of skin",

    "blocked nose": "nasal congestion",
    "stuffy nose": "nasal congestion",

    "runny nose": "coryza",

    "sore throat": "sore throat",

    "chest pain": "sharp chest pain",

    "back ache": "back pain",
    "backache": "back pain",
}


# ============================================================
# LOAD MODEL DATA
# ============================================================

def load_model_data():

    print("Loading AI HealthMate model...")

    model = joblib.load(MODEL_PATH)

    X_train = pd.read_csv(
        PROCESSED_DIR / "X_train.csv",
        nrows=1
    )

    symptoms = X_train.columns.tolist()

    label_mapping = pd.read_csv(
        PROCESSED_DIR / "label_mapping.csv"
    )

    label_map = dict(
        zip(
            label_mapping["encoded_label"],
            label_mapping["disease"]
        )
    )

    print("Model loaded successfully!")
    print(f"Total symptoms available: {len(symptoms)}")

    return model, symptoms, label_map


# ============================================================
# NORMALIZE USER SYMPTOM
# ============================================================

def normalize_symptom(user_symptom, symptoms):

    symptom_lookup = {
        symptom.strip().lower(): symptom
        for symptom in symptoms
    }

    normalized_input = user_symptom.strip().lower()

    # Direct match
    if normalized_input in symptom_lookup:
        return symptom_lookup[normalized_input]

    # Alias match
    if normalized_input in SYMPTOM_ALIASES:

        target = SYMPTOM_ALIASES[normalized_input]

        if target.lower() in symptom_lookup:
            return symptom_lookup[target.lower()]

    return None


# ============================================================
# PREDICT DISEASE
# ============================================================

def predict_disease(
    model,
    symptoms,
    label_map,
    selected_symptoms
):

    # --------------------------------------------------------
    # Create symptom-to-index lookup
    # --------------------------------------------------------

    symptom_index = {
        symptom: index
        for index, symptom in enumerate(symptoms)
    }

    # --------------------------------------------------------
    # Create feature vector
    # --------------------------------------------------------

    input_data = [0] * len(symptoms)

    for symptom in selected_symptoms:

        if symptom in symptom_index:

            index = symptom_index[symptom]

            input_data[index] = 1

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    input_df = pd.DataFrame(
        [input_data],
        columns=symptoms
    )

    # --------------------------------------------------------
    # Predict disease
    # --------------------------------------------------------

    prediction = model.predict(input_df)[0]

    disease = label_map[prediction]

    # --------------------------------------------------------
    # Calculate model score
    # --------------------------------------------------------

    probabilities = model.predict_proba(input_df)[0]

    confidence = probabilities[prediction]

    # --------------------------------------------------------
    # Get top 3 predictions
    # --------------------------------------------------------

    top_indices = probabilities.argsort()[-3:][::-1]

    top_predictions = []

    for index in top_indices:

        predicted_disease = label_map[index]

        score = probabilities[index] * 100

        top_predictions.append(
            (
                predicted_disease,
                score
            )
        )

    return (
        disease,
        confidence * 100,
        top_predictions
    )


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    model, symptoms, label_map = load_model_data()

    print("\nEnter symptoms separated by commas.")

    user_input = input("\nEnter symptoms: ")

    entered_symptoms = [
        symptom.strip()
        for symptom in user_input.split(",")
        if symptom.strip()
    ]

    selected_symptoms = []
    unrecognized_symptoms = []

    for symptom in entered_symptoms:

        actual_symptom = normalize_symptom(
            symptom,
            symptoms
        )

        if actual_symptom:

            if actual_symptom not in selected_symptoms:
                selected_symptoms.append(actual_symptom)

        else:

            if symptom not in unrecognized_symptoms:
                unrecognized_symptoms.append(symptom)

    print("\n" + "=" * 70)
    print("SYMPTOM INPUT RESULTS")
    print("=" * 70)

    print("\nRecognized symptoms:")

    if selected_symptoms:

        for symptom in selected_symptoms:
            print(f"✓ {symptom}")

    else:

        print("None")

    if unrecognized_symptoms:

        print("\nUnrecognized symptoms:")

        for symptom in unrecognized_symptoms:
            print(f"✗ {symptom}")

    if not selected_symptoms:

        print("\nNo valid symptoms were entered.")
        raise SystemExit

    print("\nPredicting disease...")

    disease, confidence, top_predictions = predict_disease(
        model,
        symptoms,
        label_map,
        selected_symptoms
    )

    print("\n" + "=" * 70)
    print("AI HEALTHMATE PREDICTION")
    print("=" * 70)

    print(f"\nPredicted disease: {disease}")

    print(
        f"Model confidence score: "
        f"{confidence:.2f}%"
    )

    print("\nTop 3 possible predictions:")

    for rank, (predicted_disease, score) in enumerate(
        top_predictions,
        start=1
    ):

        print(
            f"{rank}. {predicted_disease} "
            f"({score:.2f}%)"
        )

    print("\nSelected symptoms:")

    for symptom in selected_symptoms:
        print(f"- {symptom}")

    print("\n" + "=" * 70)
    print(
        "DISCLAIMER: This prediction is for educational and "
        "decision-support purposes only."
    )

    print(
        "It is not a medical diagnosis. Consult a qualified "
        "healthcare professional for medical advice."
    )

    print("=" * 70)