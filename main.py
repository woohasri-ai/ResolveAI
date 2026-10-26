
from pathlib import Path

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator


# 1. Create the FastAPI application
app = FastAPI(
    title="ResolveAI API",
    description="AI-powered customer operations copilot",
    version="0.2.0",
)


# 2. Load the saved machine-learning model
MODEL_PATH = (
    Path(__file__).parent
    / "Data"
    / "escalation_baseline_model.joblib"
)

model = joblib.load(MODEL_PATH)


# 3. Priority classification rules
SECURITY_KEYWORDS = [
    "security breach",
    "data breach",
    "account hacked",
    "account has been hacked",
    "hacked",
    "fraud",
    "unauthorized access",
    "payment stolen",
]

INDEPENDENT_HIGH_PRIORITY_KEYWORDS = [
    "service outage",
    "service is down",
    "service is unavailable",
    "system down",
    "platform is down",
    "unable to use the service",
    "cannot access the application",
    "cannot access my account",
]

MEDIUM_PRIORITY_KEYWORDS = [
    "refund",
    "charged twice",
    "payment failed",
    "billing issue",
    "unable to log in",
    "login issue",
    "order delayed",
    "subscription cancelled",
]

SECURITY_NEGATION_PHRASES = [
    "not hacked",
    "was not hacked",
    "has not been hacked",
    "never hacked",
    "no security breach",
    "no data breach",
    "not a fraud",
    "no unauthorized access",
]


# 4. Shared validation for ticket descriptions
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
            raise ValueError(
                "Issue description cannot be empty or whitespace"
            )

        return value


# Separate request schema for priority classification
class PriorityRequest(TicketRequest):
    pass


# 5. Check whether the API is running
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResolveAI API",
    }


# 6. Check whether the ML model is loaded
@app.get("/model-health")
def model_health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


# 7. Predict whether a ticket may require escalation
@app.post("/predict")
def predict_escalation(request: TicketRequest):
    description = request.issue_description

    probabilities = model.predict_proba([description])[0]

    # Find the probability corresponding to the "Yes" class
    yes_column = list(model.classes_).index("Yes")
    escalation_probability = float(probabilities[yes_column])

    # Baseline decision threshold
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


# 8. Classify ticket priority using local rules
@app.post("/priority")
def classify_priority(request: PriorityRequest):
    description = request.issue_description.lower()

    has_negated_security_keyword = any(
        phrase in description
        for phrase in SECURITY_NEGATION_PHRASES
    )

    has_security_keyword = any(
        keyword in description
        for keyword in SECURITY_KEYWORDS
    )

    has_independent_high_priority_keyword = any(
        keyword in description
        for keyword in INDEPENDENT_HIGH_PRIORITY_KEYWORDS
    )

    # Independent urgent incidents take precedence.
    # Security keywords trigger High unless a configured
    # security-negation phrase is present.
    has_high_priority_keyword = (
        has_independent_high_priority_keyword
        or (
            has_security_keyword
            and not has_negated_security_keyword
        )
    )

    if has_high_priority_keyword:
        priority = "High"
        reason = "The ticket contains a high-urgency keyword."

    elif any(
        keyword in description
        for keyword in MEDIUM_PRIORITY_KEYWORDS
    ):
        priority = "Medium"
        reason = "The ticket contains a moderate-urgency keyword."

    else:
        priority = "Low"
        reason = (
            "No configured high- or medium-urgency keyword was found."
        )

    return {
        "issue_description": request.issue_description,
        "priority": priority,
        "reason": reason,
        "classification_method": "Rule-based keyword matching",
    }
