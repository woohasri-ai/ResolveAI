
from pathlib import Path

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

# 1. Create the FastAPI application
app = FastAPI(
    title="ResolveAI API",
    description="AI-powered customer operations copilot",
    version="0.1.0",
)

# 2. Load the saved machine-learning model
MODEL_PATH = (
    Path(__file__).parent
    / "Data"
    / "escalation_baseline_model.joblib"
)

model = joblib.load(MODEL_PATH)


# 3. Validate incoming ticket descriptions

from pydantic import BaseModel, Field, field_validator


class TicketRequest(BaseModel):
    issue_description: str = Field(
        min_length=5,
        max_length=5000,
        description="Description of the customer's support issue",
    )

    @field_validator("issue_description")
    @classmethod
    def validate_issue_description(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Issue description cannot be empty or whitespace")

        return value



# 4. Check whether the API is running
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResolveAI API",
    }


# 5. Check whether the ML model is loaded
@app.get("/model-health")
def model_health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


# 6. Predict whether a ticket may require escalation
@app.post("/predict")
def predict_escalation(request: TicketRequest):
    description = request.issue_description.strip()

    probabilities = model.predict_proba([description])[0]

    # Find the probability corresponding to the "Yes" class
    yes_column = list(model.classes_).index("Yes")
    escalation_probability = float(probabilities[yes_column])

    # Use the 0.40 threshold from our baseline experiment
    threshold = 0.40

    prediction = (
        "Yes"
        if escalation_probability >= threshold
        else "No"
    )

    return {
        "issue_description": description,
        "predicted_escalation": prediction,
        "escalation_probability": round(
            escalation_probability, 4
        ),
        "decision_threshold": threshold,
        "model_type": "TF-IDF + Logistic Regression",
    }


def test_predict_trims_description_whitespace():
    response = client.post(
        "/predict",
        json={
            "issue_description": (
                "   I was charged twice for my subscription.   "
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["issue_description"] == (
        "I was charged twice for my subscription."
    )
