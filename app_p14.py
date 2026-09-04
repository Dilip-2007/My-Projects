import streamlit as st

from triage_engine import classify_ticket
from response_generator import generate_response


# ---------------------------------------
# Page configuration
# ---------------------------------------

st.set_page_config(
    page_title="Autonomous Customer Support Agent",
    page_icon="🎫",
    layout="wide"
)


# ---------------------------------------
# Header
# ---------------------------------------

st.title("🎫 Autonomous Customer Support & Ticket Routing Agent")

st.caption(
    "Gemini 3.6 Flash • AI-powered triage, routing and response drafting"
)


# ---------------------------------------
# Session state
# ---------------------------------------

if "triage" not in st.session_state:
    st.session_state.triage = None

if "response" not in st.session_state:
    st.session_state.response = None


# ---------------------------------------
# Customer email input
# ---------------------------------------

st.subheader("📨 Customer Email")

customer_email = st.text_area(
    "Incoming customer message",
    height=180,
    placeholder="Paste a customer support email here..."
)


# ---------------------------------------
# Analyze button
# ---------------------------------------

if st.button("🔍 Analyze & Route Ticket", type="primary"):

    if not customer_email.strip():

        st.warning("Please enter a customer email first.")

    else:

        with st.spinner("Analyzing ticket with Gemini..."):

            try:

                triage = classify_ticket(customer_email)

                response = generate_response(
                    customer_email,
                    triage
                )

                st.session_state.triage = triage
                st.session_state.response = response

                st.success("Ticket successfully classified and routed.")

            except Exception as e:

                st.error(f"Error: {e}")


# ---------------------------------------
# Display results
# ---------------------------------------

if st.session_state.triage:

    triage = st.session_state.triage

    st.divider()

    st.subheader("📊 Ticket Triage")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Department",
            triage.department
        )

    with col2:
        st.metric(
            "Priority",
            triage.priority
        )

    with col3:
        st.metric(
            "Sentiment",
            triage.sentiment
        )

    with col4:
        st.metric(
            "SLA",
            f"{triage.sla_response_hours} hrs"
        )

    st.subheader("🧠 AI Reasoning")

    st.info(triage.reasoning)


    # ---------------------------------------
    # Response draft
    # ---------------------------------------

    st.subheader("✉️ Draft Response")

    edited_response = st.text_area(
        "Review and edit before sending",
        value=st.session_state.response,
        height=250
    )


    # ---------------------------------------
    # Approve / Send simulation
    # ---------------------------------------

    if st.button("✅ Approve & Send", type="primary"):

        st.success(
            "Response approved and sent successfully! "
            "(Simulation)"
        )

        st.write("### Sent Message")

        st.write(edited_response)