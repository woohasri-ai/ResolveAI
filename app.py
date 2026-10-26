import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="ResolveAI",
    page_icon="🤖",
    layout="wide",
)

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Page header
st.title("🤖 ResolveAI")
st.subheader("AI-Powered Customer Operations Copilot")

st.write(
    "Analyze customer support tickets using machine learning "
    "for escalation prediction and rule-based priority classification."
)

st.divider()

# Ticket input
st.header("🎫 Analyze a Customer Support Ticket")

issue_description = st.text_area(
    "Describe the customer's issue",
    placeholder=(
        "Example: The customer was charged twice for the same order."
    ),
    height=150,
    max_chars=5000,
)

analyze_button = st.button(
    "🔍 Analyze Ticket",
    type="primary",
    use_container_width=True,
)

# Analyze the ticket
if analyze_button:
    if not issue_description.strip():
        st.warning("Please enter a customer issue before analyzing.")

    elif len(issue_description.strip()) < 5:
        st.warning("Please enter at least 5 characters describing the issue.")

    else:
        try:
            with st.spinner("Analyzing the customer ticket..."):
                # Escalation prediction
                prediction_response = requests.post(
                    f"{API_BASE_URL}/predict",
                    json={"issue_description": issue_description},
                    timeout=10,
                )
                prediction_response.raise_for_status()
                prediction = prediction_response.json()

                # Priority classification
                priority_response = requests.post(
                    f"{API_BASE_URL}/priority",
                    json={"issue_description": issue_description},
                    timeout=10,
                )
                priority_response.raise_for_status()
                priority_result = priority_response.json()

            st.divider()
            st.header("📊 Analysis Results")

            # Display results side by side
            escalation_col, priority_col = st.columns(2)

            with escalation_col:
                st.subheader("Escalation Prediction")

                predicted_escalation = prediction["predicted_escalation"]
                probability = prediction["escalation_probability"]

                if predicted_escalation == "Yes":
                    st.error("🚨 Escalation: Yes")
                else:
                    st.success("✅ Escalation: No")

                st.metric(
                    label="Escalation Probability",
                    value=f"{probability:.2%}",
                )

                st.progress(
                    max(0.0, min(1.0, float(probability)))
                )

                st.caption(
                    f"Decision threshold: "
                    f"{prediction['decision_threshold']:.0%}"
                )

                st.caption(
                    f"Model: {prediction['model_type']}"
                )

            with priority_col:
                st.subheader("Ticket Priority")

                priority = priority_result["priority"]

                if priority == "High":
                    st.error(f"🔴 Priority: {priority}")
                elif priority == "Medium":
                    st.warning(f"🟠 Priority: {priority}")
                else:
                    st.success(f"🟢 Priority: {priority}")

                st.write("**Reason:**")
                st.write(priority_result["reason"])

                st.caption(
                    f"Method: {priority_result['classification_method']}"
                )

            st.divider()
            st.caption(
                "ResolveAI provides decision support. "
                "Review predictions before taking action."
            )

        except requests.Timeout:
            st.error(
                "The ResolveAI API took too long to respond. "
                "Please try again."
            )

        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else "unknown"
            )
            st.error(
                f"The API returned an HTTP error ({status_code}). "
                "Please check the API response and try again."
            )

        except requests.RequestException:
            st.error(
                "Could not connect to the ResolveAI API. "
                "Please make sure the FastAPI server is running."
            )

        except (KeyError, TypeError, ValueError):
            st.error(
                "The API returned an unexpected response. "
                "Please check the backend response format."
            )