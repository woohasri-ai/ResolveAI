
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_model_health_endpoint():
    response = client.get("/model-health")

    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


def test_predict_endpoint():
    response = client.post(
        "/predict",
        json={
            "issue_description": (
                "I was charged twice for the same subscription "
                "and need a refund."
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["predicted_escalation"] in ["Yes", "No"]
    assert 0.0 <= result["escalation_probability"] <= 1.0
    assert result["decision_threshold"] == 0.40


def test_predict_rejects_short_description():
    response = client.post(
        "/predict",
        json={"issue_description": "Hi"},
    )

    assert response.status_code == 422


def test_predict_rejects_long_description():
    response = client.post(
        "/predict",
        json={"issue_description": "A" * 5001},
    )

    assert response.status_code == 422
    

def test_predict_rejects_missing_description():
    response = client.post(
        "/predict",
        json={},
    )

    assert response.status_code == 422
    

def test_predict_rejects_whitespace_only_description():
    response = client.post(
        "/predict",
        json={"issue_description": "     "},
    )

    assert response.status_code == 422


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
    

def test_predict_probability_is_rounded_to_four_decimals():
    response = client.post(
        "/predict",
        json={
            "issue_description": (
                "I was charged twice for the same subscription "
                "and need a refund."
            )
        },
    )

    assert response.status_code == 200

    probability = response.json()["escalation_probability"]

    assert isinstance(probability, float)
    assert round(probability, 4) == probability


def test_prediction_matches_probability_threshold():
    response = client.post(
        "/predict",
        json={
            "issue_description": (
                "I was charged twice for the same subscription "
                "and need a refund."
            )
        },
    )

    assert response.status_code == 200

    result = response.json()
    probability = result["escalation_probability"]
    prediction = result["predicted_escalation"]
    threshold = result["decision_threshold"]

    if probability >= threshold:
        assert prediction == "Yes"
    else:
        assert prediction == "No"

def test_priority_endpoint_classifies_hacked_account_as_high():
    response = client.post(
        "/priority",
        json={
            "issue_description": (
                "My account has been hacked and someone "
                "accessed my personal data."
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["priority"] == "High"
    assert result["classification_method"] == (
        "Rule-based keyword matching"
    )

def test_priority_endpoint_classifies_billing_issue_as_medium():
    response = client.post(
        "/priority",
        json={
            "issue_description": (
                "I was charged twice for my subscription "
                "and need a refund."
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["priority"] == "Medium"

def test_priority_endpoint_classifies_profile_question_as_low():
    response = client.post(
        "/priority",
        json={
            "issue_description": (
                "How can I change the display name on my profile?"
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["priority"] == "Low"

def test_priority_endpoint_rejects_short_description():
    response = client.post(
        "/priority",
        json={"issue_description": "Hi"},
    )

    assert response.status_code == 422


def test_priority_endpoint_rejects_long_description():
    response = client.post(
        "/priority",
        json={"issue_description": "A" * 5001},
    )

    assert response.status_code == 422

def test_priority_endpoint_rejects_missing_description():
    response = client.post(
        "/priority",
        json={},
    )

    assert response.status_code == 422

def test_priority_endpoint_rejects_whitespace_only_description():
    response = client.post(
        "/priority",
        json={"issue_description": "     "},
    )

    assert response.status_code == 422
def test_priority_endpoint_does_not_flag_negated_hacking_as_high():
    response = client.post(
        "/priority",
        json={
            "issue_description": (
                "My account was not hacked. "
                "I just want to update my profile."
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["priority"] == "Low"