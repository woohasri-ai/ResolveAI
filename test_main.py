
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
