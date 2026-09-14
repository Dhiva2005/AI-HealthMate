from pathlib import Path
import sys


# ============================================================
# PATH CONFIGURATION
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from predict import (
    load_model_data,
    normalize_symptom,
    predict_disease,
)

from recommend import get_recommendations


# ============================================================
# SAFETY CONFIGURATION
# ============================================================

MIN_SYMPTOMS_WARNING = 2
LOW_CONFIDENCE_THRESHOLD = 50.0


# ============================================================
# EMERGENCY / RED-FLAG SYMPTOMS
# ============================================================

# These symptoms do not diagnose an emergency.
# They only trigger a safety warning asking the user to
# seek urgent professional medical attention.

EMERGENCY_SYMPTOMS = {
    "chest pain",
    "sharp chest pain",
    "difficulty breathing",
    "shortness of breath",
    "severe breathing difficulty",
    "loss of consciousness",
    "fainting",
    "severe bleeding",
    "vomiting blood",
    "blood in stool",
    "severe abdominal pain",
    "sudden severe headache",
    "weakness of one side of body",
    "slurred speech",
    "seizures",
}


# ============================================================
# HEALTHMATE SERVICE
# ============================================================

class HealthMateService:

    def __init__(self):
        """
        Initialize the AI HealthMate service.

        Loads:
        - trained Random Forest model
        - symptom list
        - disease label mapping
        """

        self.model, self.symptoms, self.label_map = load_model_data()

    # ========================================================
    # CONFIDENCE LEVEL
    # ========================================================

    def get_confidence_level(self, model_score):
        """
        Convert the model score into a simple confidence level.

        IMPORTANT:
        This is a model score, not a clinical probability.
        """

        if model_score >= 70:
            return "high"

        if model_score >= 50:
            return "moderate"

        return "low"

    # ========================================================
    # EMERGENCY / RED-FLAG CHECK
    # ========================================================

    def check_emergency_symptoms(self, symptoms):
        """
        Check whether any provided symptom matches a
        red-flag symptom.

        The check is performed using the original user
        symptom text so that emergency symptoms do not
        need to exist in the ML dataset.

        Returns:
            emergency_warning: bool
            emergency_matches: list
        """

        emergency_matches = []

        for symptom in symptoms:

            if symptom is None:
                continue

            normalized = str(symptom).strip().lower()

            if not normalized:
                continue

            if normalized in EMERGENCY_SYMPTOMS:

                if normalized not in emergency_matches:
                    emergency_matches.append(normalized)

        return (
            len(emergency_matches) > 0,
            emergency_matches
        )

    # ========================================================
    # MAIN PROCESSING FUNCTION
    # ========================================================

    def process_symptoms(self, user_symptoms):

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not user_symptoms:
            raise ValueError(
                "No symptoms were provided. "
                "Please enter at least one symptom."
            )

        # ----------------------------------------------------
        # Remove empty values from input
        # ----------------------------------------------------

        cleaned_user_symptoms = []

        for symptom in user_symptoms:

            if symptom is None:
                continue

            symptom = str(symptom).strip()

            if symptom:
                cleaned_user_symptoms.append(symptom)

        # ----------------------------------------------------
        # Validate after cleaning
        # ----------------------------------------------------

        if not cleaned_user_symptoms:
            raise ValueError(
                "No symptoms were provided. "
                "Please enter at least one valid symptom."
            )

        # ----------------------------------------------------
        # Emergency / red-flag check
        # ----------------------------------------------------

        # This is done before normalization so that a red-flag
        # symptom can trigger a warning even if it is not one
        # of the ML model's 230 symptoms.

        emergency_warning, emergency_symptoms = (
            self.check_emergency_symptoms(
                cleaned_user_symptoms
            )
        )

        if emergency_warning:

            emergency_warning_message = (
                "Some reported symptoms may require urgent "
                "medical attention. Please seek immediate "
                "professional medical care rather than relying "
                "on this prediction."
            )

        else:

            emergency_warning_message = None

        # ----------------------------------------------------
        # Normalize symptoms for ML model
        # ----------------------------------------------------

        recognized_symptoms = []
        unrecognized_symptoms = []

        for symptom in cleaned_user_symptoms:

            normalized = normalize_symptom(
                symptom,
                self.symptoms
            )

            if normalized:

                if normalized not in recognized_symptoms:
                    recognized_symptoms.append(normalized)

            else:

                if symptom not in unrecognized_symptoms:
                    unrecognized_symptoms.append(symptom)

        # ----------------------------------------------------
        # Check whether at least one symptom was recognized
        # ----------------------------------------------------

        if not recognized_symptoms:
            raise ValueError(
                "No recognized symptoms were provided. "
                "Please enter valid symptoms."
            )

        # ----------------------------------------------------
        # Minimum symptom warning
        # ----------------------------------------------------

        symptom_warning = (
            len(recognized_symptoms) < MIN_SYMPTOMS_WARNING
        )

        if symptom_warning:

            symptom_warning_message = (
                "Prediction may be unreliable because fewer "
                "than 2 recognized symptoms were provided."
            )

        else:

            symptom_warning_message = None

        # ----------------------------------------------------
        # Predict disease
        # ----------------------------------------------------

        (
            disease,
            model_score,
            top_predictions
        ) = predict_disease(
            self.model,
            self.symptoms,
            self.label_map,
            recognized_symptoms
        )

        # ----------------------------------------------------
        # Determine confidence level
        # ----------------------------------------------------

        confidence_level = self.get_confidence_level(
            model_score
        )

        # ----------------------------------------------------
        # Low-confidence warning
        # ----------------------------------------------------

        confidence_warning = (
            model_score < LOW_CONFIDENCE_THRESHOLD
        )

        if confidence_warning:

            confidence_warning_message = (
                "The model score is low. This prediction may "
                "be unreliable and should not be treated as "
                "a medical diagnosis."
            )

        else:

            confidence_warning_message = None

        # ----------------------------------------------------
        # Format top predictions
        # ----------------------------------------------------

        top_prediction_data = []

        for prediction_disease, prediction_score in top_predictions:

            top_prediction_data.append(
                {
                    "disease": prediction_disease,
                    "model_score": round(
                        prediction_score,
                        2
                    )
                }
            )

        # ----------------------------------------------------
        # Get health recommendations
        # ----------------------------------------------------

        recommendations = get_recommendations(
            disease
        )

        # ----------------------------------------------------
        # Return complete structured response
        # ----------------------------------------------------

        return {

            # Prediction
            "predicted_disease": disease,

            "model_score": round(
                model_score,
                2
            ),

            # Confidence
            "confidence_level": confidence_level,

            "confidence_warning": confidence_warning,

            "confidence_warning_message": (
                confidence_warning_message
            ),

            # Alternative predictions
            "top_predictions": top_prediction_data,

            # Symptoms
            "recognized_symptoms": recognized_symptoms,

            "unrecognized_symptoms": unrecognized_symptoms,

            # Minimum symptom warning
            "symptom_warning": symptom_warning,

            "symptom_warning_message": (
                symptom_warning_message
            ),

            # Emergency safety
            "emergency_warning": emergency_warning,

            "emergency_warning_message": (
                emergency_warning_message
            ),

            "emergency_symptoms": emergency_symptoms,

            # Health recommendations
            "description": recommendations["description"],

            "medications": recommendations["medications"],

            "precautions": recommendations["precautions"],

            "diet": recommendations["diet"],

            "workout": recommendations["workout"],
        }


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI HEALTHMATE SERVICE TEST")
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # Create service
        # ----------------------------------------------------

        service = HealthMateService()

        # ----------------------------------------------------
        # Test symptoms
        # ----------------------------------------------------

        test_symptoms = [
            "fever",
            "headache",
            "vomiting"
        ]

        # ----------------------------------------------------
        # Process symptoms
        # ----------------------------------------------------

        result = service.process_symptoms(
            test_symptoms
        )

        # ----------------------------------------------------
        # Display prediction
        # ----------------------------------------------------

        print("\nPredicted Disease:")
        print(
            result["predicted_disease"]
        )

        # ----------------------------------------------------
        # Display model score
        # ----------------------------------------------------

        print("\nModel Score:")
        print(
            f'{result["model_score"]}%'
        )

        # ----------------------------------------------------
        # Display confidence
        # ----------------------------------------------------

        print("\nConfidence Level:")
        print(
            result["confidence_level"]
        )

        print("\nConfidence Warning:")
        print(
            result["confidence_warning"]
        )

        print("\nConfidence Warning Message:")
        print(
            result["confidence_warning_message"]
        )

        # ----------------------------------------------------
        # Display recognized symptoms
        # ----------------------------------------------------

        print("\nRecognized Symptoms:")
        print(
            result["recognized_symptoms"]
        )

        # ----------------------------------------------------
        # Display unrecognized symptoms
        # ----------------------------------------------------

        print("\nUnrecognized Symptoms:")
        print(
            result["unrecognized_symptoms"]
        )

        # ----------------------------------------------------
        # Display symptom warning
        # ----------------------------------------------------

        print("\nSymptom Warning:")
        print(
            result["symptom_warning"]
        )

        print("\nSymptom Warning Message:")
        print(
            result["symptom_warning_message"]
        )

        # ----------------------------------------------------
        # Display emergency warning
        # ----------------------------------------------------

        print("\nEmergency Warning:")
        print(
            result["emergency_warning"]
        )

        print("\nEmergency Warning Message:")
        print(
            result["emergency_warning_message"]
        )

        print("\nEmergency Symptoms:")
        print(
            result["emergency_symptoms"]
        )

        # ----------------------------------------------------
        # Display top predictions
        # ----------------------------------------------------

        print("\nTop Predictions:")

        for prediction in result["top_predictions"]:

            print(
                f'  {prediction["disease"]}: '
                f'{prediction["model_score"]}%'
            )

        # ----------------------------------------------------
        # Test completed
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("SERVICE TEST COMPLETED")
        print("=" * 60)

    except Exception as error:

        print("\nService test failed:")
        print(error)