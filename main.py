from pathlib import Path
import re

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator


# 1. Create the FastAPI application
app = FastAPI(
    title="ResolveAI API",
    description="AI-powered customer operations copilot",
    version="0.3.0",
)


# 2. Load the saved machine-learning model
MODEL_PATH = (
    Path(__file__).parent
    / "Data"
    / "escalation_baseline_model.joblib"
)

model = joblib.load(MODEL_PATH)


# 3. Priority classification rules

# Security-related incidents
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

# Independent high-priority incidents, including service outages
INDEPENDENT_HIGH_PRIORITY_KEYWORDS = [
    "service outage",
    "service is down",
    "service down",
    "service is completely down",
    "service completely down",
    "service is unavailable",
    "service unavailable",
    "system down",
    "system is down",
    "platform is down",
    "platform down",
    "platform is completely down",
    "platform completely down",
    "no customers can access the platform",
    "customers cannot access the platform",
    "customers can't access the platform",
    "nobody can access the platform",
    "no one can access the platform",
    "the entire platform is down",
    "entire platform down",
    "complete outage",
    "major outage",
    "all users are affected",
    "unable to use the service",
    "cannot use the service",
    "can't use the service",
    "cannot access the application",
    "can't access the application",
    "cannot access my account",
]

# Moderate-priority incidents
MEDIUM_PRIORITY_KEYWORDS = [
    "refund",
    "charged twice",
    "payment failed",
    "billing issue",
    "unable to log in",
    "unable to login",
    "login issue",
    "order delayed",
    "subscription cancelled",
]

# Basic security-negation phrases
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


# 4. Normalize text for keyword matching
def normalize_text(text: str) -> str:
    """Normalize case, whitespace, and punctuation for matching."""
    text = text.lower()
    text = re.sub(r"[^\w\s']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# 5. Shared validation for ticket descriptions
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


class PriorityRequest(TicketRequest):
    pass


# 6. Check whether the API is running
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResolveAI API",
    }


# 7. Check whether the ML model is loaded
@app.get("/model-health")
def model_health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


# 8. Predict whether a ticket may require escalation
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


# 9. Classify ticket priority using local rules
@app.post("/priority")
def classify_priority(request: PriorityRequest):
    description = normalize_text(request.issue_description)

    # Check for a configured security-negation phrase
    has_negated_security_keyword = any(
        phrase in description
        for phrase in SECURITY_NEGATION_PHRASES
    )

    has_security_keyword = any(
        keyword in description
        for keyword in SECURITY_KEYWORDS
    )

    # Independent urgent incidents always take precedence
    has_independent_high_priority_keyword = any(
        keyword in description
        for keyword in INDEPENDENT_HIGH_PRIORITY_KEYWORDS
    )

    has_high_priority_keyword = (
        has_independent_high_priority_keyword
        or (
            has_security_keyword
            and not has_negated_security_keyword
        )
    )

    if has_high_priority_keyword:
        priority = "High"
        reason = (
            "The ticket describes a high-urgency incident "
            "or service disruption."
        )

    elif any(
        keyword in description
        for keyword in MEDIUM_PRIORITY_KEYWORDS
    ):
        priority = "Medium"
        reason = (
            "The ticket contains a moderate-urgency keyword."
        )

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
