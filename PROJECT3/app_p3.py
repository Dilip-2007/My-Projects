import streamlit as st
from google import genai
from dotenv import load_dotenv
import os


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Persona Translator",
    page_icon="🎭",
    layout="centered"
)


# -----------------------------
# Title
# -----------------------------
st.title("🎭 Persona Translator")

st.write(
    "Choose a persona and Gemini will explain your topic in that style."
)


# -----------------------------
# Get API key
# -----------------------------
api_key = os.getenv("GEMINI_API_KEY")


# -----------------------------
# Create Gemini client
# -----------------------------
client = genai.Client(api_key=api_key)


# -----------------------------
# Persona selection
# -----------------------------
persona = st.selectbox(
    "Choose a persona:",
    [
        "ELI5",
        "Ranked Gamer",
        "Gen Z Slang"
    ]
)


# -----------------------------
# Topic input
# -----------------------------
topic = st.text_area(
    "Enter a topic:",
    placeholder="Example: Inflation"
)


# -----------------------------
# Persona instructions
# -----------------------------
persona_instructions = {

    "ELI5":
        "Explain the topic as if you are explaining it to a 5-year-old. "
        "Use very simple words and easy examples.",

    "Ranked Gamer":
        "Explain the topic using competitive gaming language, "
        "ranked-game examples, XP, levels, buffs, debuffs, "
        "and other gaming concepts.",

    "Gen Z Slang":
        "Explain the topic using casual Gen Z internet language. "
        "Keep the explanation accurate but fun and easy to understand."
}


# -----------------------------
# Generate answer
# -----------------------------
if st.button("Translate with Gemini"):

    if topic.strip() == "":
        st.warning("Please enter a topic.")

    else:

        instruction = persona_instructions[persona]

        prompt = f"""
You are a helpful AI tutor.

The user wants to understand this topic:

{topic}

Your persona instructions are:

{instruction}

Give an accurate explanation.
Do not sacrifice factual correctness just to match the style.
"""

        try:

            with st.spinner("Gemini is creating the explanation..."):

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=prompt
                )

            st.subheader("🎯 Gemini's Explanation")

            st.write(response.text)

        except Exception as e:

            st.error(f"Something went wrong: {e}")