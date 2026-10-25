# ResolveAI

**An AI-powered customer operations copilot combining machine learning, FastAPI, and LLM-powered workflows.**

ResolveAI is a portfolio project focused on helping customer support teams analyze support tickets, assess escalation risk, and support customer operations through structured, AI-assisted workflows.

## Project Goals

- **Escalation prediction:** Use machine learning to estimate whether a support ticket may require escalation.
- **API-driven workflows:** Build REST APIs with FastAPI to expose customer operations functionality.
- **LLM-powered assistance:** Develop structured AI workflows for interpreting customer requests and supporting operational decisions.
- **Reliable operations:** Apply input validation, testing, and controlled business rules to make workflows more dependable.

## Current Progress

- [x] Support-ticket dataset inspection and preparation
- [x] Baseline escalation-classification model using TF-IDF and logistic regression
- [x] Group-aware train/test split to prevent identical ticket descriptions from crossing the split
- [x] Evaluation at multiple decision thresholds
- [x] Saved-model loading and prediction testing
- [x] Project files pushed to GitHub

*Note: The baseline model uses a synthetic support-ticket dataset. Its evaluation results should not be interpreted as proof of real-world performance.*

## Technology Stack

- Python
- pandas and NumPy
- scikit-learn
- TF-IDF and logistic regression
- FastAPI (planned integration)
- LLM APIs (planned integration)
- Git and GitHub

## Repository

[View the ResolveAI source code on GitHub](https://github.com/woohasri-ai/ResolveAI)
