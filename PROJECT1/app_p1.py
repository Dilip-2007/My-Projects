import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Hello World AI App",
    page_icon="🤖",
    layout="centered"
)

# Title
st.title("🤖 Hello World Web UI")

# Description
st.write("Welcome to your first AI application!")

# Get user's name
name = st.text_input("Enter your name:")

# Submit button
if st.button("Submit"):

    # Validate input
    if name.strip() == "":
        st.warning("Please enter your name.")

    else:
        st.success(
            f"Hello, {name.strip()}! Welcome to building AI apps."
        )