# ResolveAI — AI-Powered Customer Operations Copilot

ResolveAI is a portfolio project that combines machine learning, FastAPI, Streamlit, and rule-based workflows to help customer support teams analyze support tickets, estimate escalation risk, and classify ticket priority.

## Features

- **Escalation prediction:** Uses a TF-IDF and Logistic Regression baseline model to estimate whether a support ticket may require escalation.
- **Priority classification:** Assigns High, Medium, or Low priority using rule-based keyword matching.
- **Interactive web interface:** Provides a Streamlit UI for submitting tickets and viewing analysis results.
- **REST API:** Exposes prediction and classification functionality through FastAPI.
- **Input validation:** Validates ticket descriptions using Pydantic.
- **Error handling:** Handles API connection failures, timeouts, and unexpected responses in the UI.
- **Automated testing:** Tests API endpoints, input validation, model predictions, and priority-classification behavior.

## Technology Stack

- Python
- FastAPI and Uvicorn
- Streamlit
- Pydantic
- pandas and NumPy
- scikit-learn
- TF-IDF and Logistic Regression
- Joblib
- pytest and HTTPX
- Requests
- Git and GitHub

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Checks whether the API is running |
| GET | `/model-health` | Checks whether the saved model is available |
| POST | `/predict` | Predicts escalation risk |
| POST | `/priority` | Classifies ticket priority |

Interactive API documentation is available at `/docs` while the API is running.

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

### 4. Start the FastAPI backend

In the first terminal, run:

```powershell
uvicorn main:app --reload
```

The API will normally be available at:

`http://127.0.0.1:8000`

You can explore the endpoints at:

`http://127.0.0.1:8000/docs`

### 5. Start the Streamlit interface

Keep the FastAPI backend running. Open a **second terminal** in the project directory, activate the same virtual environment, and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Streamlit will display a local URL in the terminal, normally:

`http://localhost:8501`

Open that URL in your browser. Enter a customer support issue and select **Analyze Ticket** to view the escalation prediction and priority classification.

The Streamlit interface expects the FastAPI backend to be running at `http://127.0.0.1:8000`.

## Running Tests

With the virtual environment activated, run:

```powershell
python -m pytest -v
```

The current test suite contains **33 tests**, all of which passed in the latest local run.

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

Priority classification uses keyword matching and configured negation phrases. Although the rules cover common security, service-outage, billing, and refund scenarios, they may misclassify complex wording, context, or negation.

The escalation probability is a model output, not a guarantee that a ticket will or will not be escalated. The current system is a portfolio baseline and should not be treated as a production-ready customer-support decision system.

## Project Progress

- [x] Support-ticket dataset inspection and preparation
- [x] Baseline escalation-classification model using TF-IDF and Logistic Regression
- [x] Group-aware train/test split to reduce leakage from duplicate ticket descriptions
- [x] Evaluation at multiple decision thresholds
- [x] Saved-model loading and prediction tests
- [x] FastAPI health and model-health endpoints
- [x] Escalation prediction endpoint
- [x] Rule-based priority classification endpoint
- [x] Input validation and error handling
- [x] Automated backend tests — 33 passed
- [x] Streamlit interface for ticket analysis
- [x] Changes committed and pushed to GitHub

## Future Improvements

- Improve priority classification with more robust language understanding.
- Evaluate the model on representative, non-synthetic support-ticket data.
- Add more comprehensive negation and context handling.
- Add monitoring, logging, and broader integration tests.
- Consider configurable API settings and deployment options.
