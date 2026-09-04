import streamlit as st
from google import genai
from dotenv import load_dotenv
import os



# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Rule-Based Chatbot",
    page_icon="🤖",
    layout="centered"
)


# -----------------------------
# Title
# -----------------------------
st.title("🤖 Rule-Based Chatbot")

st.write(
    "Ask a common customer-support question."
)


# -----------------------------
# Chatbot rules
# -----------------------------
responses = {

    "greeting": {
        "keywords": ["hello", "hi", "hey"],
        "response": "Hello! 👋 How can I help you today?"
    },

    "thanks": {
        "keywords": ["thanks", "thank you", "thank"],
        "response": "You're welcome! 😊"
    },

    "hours": {
        "keywords": ["hours", "open", "opening", "closing"],
        "response": "Our support team is available from 9 AM to 6 PM."
    },

    "price": {
        "keywords": ["price", "cost", "pricing"],
        "response": "Please check our pricing page for the latest product prices."
    },

    "refund": {
        "keywords": ["refund", "money back", "return"],
        "response": "Refund requests can be submitted within 30 days of purchase."
    },

    "contact": {
        "keywords": ["contact", "support", "agent"],
        "response": "You can contact our support team through the support section."
    }
}


# -----------------------------
# Chatbot function
# -----------------------------
def chatbot(user_message):

    # Clean input
    message = user_message.strip().lower()

    # Check every intent
    for intent, data in responses.items():

        for keyword in data["keywords"]:

            if keyword in message:

                return data["response"]

    # Fallback response
    return (
        "I'm sorry, I don't understand that question yet. "
        "Please ask about our products, pricing, refunds, "
        "support, or opening hours."
    )


# -----------------------------
# User input
# -----------------------------
user_message = st.text_input(
    "You:",
    placeholder="Example: What are your opening hours?"
)


# -----------------------------
# Send button
# -----------------------------
if st.button("Send"):

    if user_message.strip() == "":
        st.warning("Please enter a message.")

    else:

        answer = chatbot(user_message)

        st.subheader("🤖 Bot")

        st.write(answer)