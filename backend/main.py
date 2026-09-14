from pathlib import Path
import sys
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ============================================================
# PATH CONFIGURATION
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))


# ============================================================
# IMPORT AI HEALTHMATE SERVICE
# ============================================================

from service import HealthMateService


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI HealthMate API",
    description="AI-based disease prediction and health recommendation API.",
    version="1.0.0"
)


# ============================================================
# INITIALIZE HEALTHMATE SERVICE
# ============================================================

try:
    healthmate_service = HealthMateService()
    service_error = None

except Exception as error:
    healthmate_service = None
    service_error = str(error)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class PredictionRequest(BaseModel):
    symptoms: List[str] = Field(
        ...,
        min_length=1,
        description="List of symptoms provided by the user."
    )


# ============================================================
# TOP PREDICTION SCHEMA
# ============================================================

class TopPrediction(BaseModel):
    disease: str = Field(
        ...,
        description="Predicted disease name."
    )

    model_score: float = Field(
        ...,
        description=(
            "Random Forest model score for the prediction. "
            "This is not a clinical probability."
        )
    )


# ============================================================
# RESPONSE SCHEMA
# ============================================================

class PredictionResponse(BaseModel):

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    predicted_disease: str

    model_score: float

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence_level: str

    confidence_warning: bool

    confidence_warning_message: Optional[str]

    # --------------------------------------------------------
    # Top predictions
    # --------------------------------------------------------

    top_predictions: List[TopPrediction]

    # --------------------------------------------------------
    # Symptoms
    # --------------------------------------------------------

    recognized_symptoms: List[str]

    unrecognized_symptoms: List[str]

    # --------------------------------------------------------
    # Symptom warning
    # --------------------------------------------------------

    symptom_warning: bool

    symptom_warning_message: Optional[str]

    # --------------------------------------------------------
    # Emergency safety
    # --------------------------------------------------------

    emergency_warning: bool

    emergency_warning_message: Optional[str]

    emergency_symptoms: List[str]

    # --------------------------------------------------------
    # Health recommendations
    # --------------------------------------------------------

    description: str

    medications: List[str]

    precautions: List[str]

    diet: List[str]

    workout: List[str]


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AI HealthMate API is running.",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK ENDPOINT
# ============================================================

@app.get("/health")
def health_check():

    if healthmate_service is None:

        return {
            "status": "unhealthy",
            "service": "AI HealthMate",
            "error": service_error
        }

    return {
        "status": "healthy",
        "service": "AI HealthMate"
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict Disease",
    description=(
        "Predict a disease from the provided symptoms "
        "and return health recommendations."
    )
)
def predict_disease(request: PredictionRequest):

    # --------------------------------------------------------
    # Check service availability
    # --------------------------------------------------------

    if healthmate_service is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "AI HealthMate service is unavailable. "
                "Please check the server logs."
            )
        )


    # --------------------------------------------------------
    # Process symptoms
    # --------------------------------------------------------

    try:

        result = healthmate_service.process_symptoms(
            request.symptoms
        )

        return result


    # --------------------------------------------------------
    # Handle invalid symptom input
    # --------------------------------------------------------

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    # --------------------------------------------------------
    # Handle unexpected errors
    # --------------------------------------------------------

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred while "
                "processing the prediction."
            )
        )

