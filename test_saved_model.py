import joblib

# 1. Configuration
MODEL_PATH = "Data/escalation_baseline_model.joblib"
THRESHOLD = 0.40

# 2. Load the saved model
print("Loading saved model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")

# 3. Prepare sample tickets
sample_tickets = [
    "I cannot log in to my account after resetting my password.",
    "I was charged twice for the same subscription."
]

# 4. Generate probabilities for all tickets
probabilities = model.predict_proba(sample_tickets)

# Find the probability column corresponding to "Yes"
yes_column = list(model.classes_).index("Yes")

# 5. Apply the decision threshold and display results
print(f"\nDecision threshold: {THRESHOLD:.2f}")

for index, ticket in enumerate(sample_tickets):
    escalation_probability = probabilities[index][yes_column]

    prediction = (
        "Yes"
        if escalation_probability >= THRESHOLD
        else "No"
    )

    print(f"\nTicket {index + 1}: {ticket}")
    print("Predicted escalation:", prediction)
    print(
        "Escalation probability:",
        f"{escalation_probability:.4f}"
    )

print("\nPrediction testing completed.")