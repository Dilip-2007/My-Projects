import streamlit as st
from google import genai
from dotenv import load_dotenv
import os


# --------------------------------
# Load environment variables
# --------------------------------
load_dotenv()


# --------------------------------
# Page configuration
# --------------------------------
st.set_page_config(
    page_title="AI Chatbot with Memory",
    page_icon="🧠",
    layout="centered"
)


# --------------------------------
# Get API key
# --------------------------------
api_key = os.getenv("GEMINI_API_KEY")


if not api_key:

    st.error(
        "GEMINI_API_KEY is missing. "
        "Please check your .env file."
    )

    st.stop()


# --------------------------------
# Create Gemini client
# --------------------------------
client = genai.Client(
    api_key=api_key
)


# --------------------------------
# Initialize chat history
# --------------------------------
if "messages" not in st.session_state:

    st.session_state.messages = []


# --------------------------------
# Title
# --------------------------------
st.title("🧠 AI Chatbot with Memory")

st.write(
    "Have a conversation with Gemini. "
    "The chatbot remembers previous messages."
)


# --------------------------------
# Sidebar
# --------------------------------
with st.sidebar:

    st.header("💬 Chat Controls")

    st.write(
        "Messages in this session:"
    )

    st.write(
        len(st.session_state.messages)
    )


    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()


# --------------------------------
# Display previous messages
# --------------------------------
for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# --------------------------------
# Chat input
# --------------------------------
user_message = st.chat_input(
    "Type your message..."
)


# --------------------------------
# Process user message
# --------------------------------
if user_message:

    # --------------------------------
    # Save user message
    # --------------------------------
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    # --------------------------------
    # Display user message
    # --------------------------------
    with st.chat_message("user"):

        st.write(user_message)


    try:

        # --------------------------------
        # Create conversation history
        # --------------------------------
        conversation = []

        for message in st.session_state.messages:

            conversation.append(
                f"{message['role']}: "
                f"{message['content']}"
            )


        conversation_text = "\n".join(
            conversation
        )


        # --------------------------------
        # Prompt Gemini
        # --------------------------------
        prompt = f"""
You are a helpful conversational AI assistant.

You have access to the conversation history below.

Use the previous messages to understand context
and remember important information.

Conversation history:

{conversation_text}

Now respond to the user's latest message.

Be helpful, natural, and concise.
"""


        # --------------------------------
        # Generate response
        # --------------------------------
        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=prompt
                )


            assistant_message = response.text

            st.write(
                assistant_message
            )


        # --------------------------------
        # Save assistant response
        # --------------------------------
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_message
            }
        )


    except Exception as e:

        st.error(
            f"Something went wrong: {e}"
        )