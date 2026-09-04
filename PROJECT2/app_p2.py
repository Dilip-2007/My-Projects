import streamlit as st
from google import genai

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Gemini AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# -----------------------------
# Title
# -----------------------------
st.title("🤖 Gemini AI Assistant")

st.write("Ask Gemini a question!")

# -----------------------------
# Get API key
# -----------------------------
api_key = st.secrets["GEMINI_API_KEY"]



# -----------------------------
# Create Gemini client
# -----------------------------
client = genai.Client(api_key=api_key)

# -----------------------------
# User question
# -----------------------------
question = st.text_area(
    "Enter your question:",
    placeholder="Example: Why is the sky blue?"
)

# -----------------------------
# Ask Gemini
# -----------------------------
if st.button("Ask Gemini"):

    if question.strip() == "":
        st.warning("Please enter a question.")

    else:
        try:
            with st.spinner("Gemini is thinking..."):

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=question
                )

            st.subheader("Gemini's Answer")

            st.write(response.text)

        except Exception as e:
            st.error(f"Something went wrong: {e}")
