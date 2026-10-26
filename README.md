# ResolveAI — AI-Powered Customer Operations Copilot

ResolveAI is a portfolio project that combines machine learning, FastAPI, and rule-based workflows to help customer support teams analyze support tickets, estimate escalation risk, and classify ticket priority.

## Features

- **Escalation prediction:** Uses a TF-IDF and Logistic Regression baseline model to estimate whether a support ticket may require escalation.
- **Priority classification:** Assigns High, Medium, or Low priority using rule-based keyword matching.
- **REST API:** Exposes prediction and classification functionality through FastAPI.
- **Input validation:** Validates ticket descriptions using Pydantic.
- **Automated testing:** Tests API endpoints, input validation, model predictions, and priority-classification behavior.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Checks whether the API is running |
| GET | `/model-health` | Checks whether the saved model is available |
| POST | `/predict` | Predicts escalation risk |
| POST | `/priority` | Classifies ticket priority |

Interactive API documentation is available at `/docs` while the application is running.

## Technology Stack

- Python
- FastAPI and Uvicorn
- Pydantic
- pandas and NumPy
- scikit-learn
- TF-IDF and Logistic Regression
- Joblib
- pytest and HTTPX
- Git and GitHub

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/woohasri-ai/ResolveAI.git
cd ResolveAI
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the API

```powershell
uvicorn main:app --reload
```

The API will normally be available at `http://127.0.0.1:8000`.

Open `http://127.0.0.1:8000/docs` to explore and test the endpoints interactively.

## Running Tests

With the virtual environment activated, run:

```powershell
python -m pytest -v
```

## Example Requests

### Escalation prediction

Send a `POST` request to `/predict`:

```json
{
  "issue_description": "The customer cannot access their account after repeated login failures."
}
```

### Priority classification

Send a `POST` request to `/priority`:

```json
{
  "issue_description": "The payment was charged twice."
}
```

Use the interactive API documentation at `/docs` to execute these requests and inspect the actual responses.

## Model and Data Limitations

The baseline escalation model was trained on a synthetic support-ticket dataset. Its evaluation results should not be interpreted as evidence of real-world performance.

Priority classification currently uses keyword matching and configured negation phrases. It is a simple baseline and may misclassify complex wording or context. It should not be treated as a production-ready customer-support decision system.

## Project Progress

- [x] Support-ticket dataset inspection and preparation
- [x] Baseline escalation-classification model using TF-IDF and Logistic Regression
- [x] Group-aware train/test split to reduce leakage from duplicate ticket descriptions
- [x] Evaluation at multiple decision thresholds
- [x] Saved-model loading and prediction tests
- [x] FastAPI health and model-health