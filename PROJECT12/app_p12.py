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
    page_title="Multimodal File Inspector",
    page_icon="🔍",
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
# Title
# --------------------------------
st.title("🔍 Multimodal Document & Code Inspector")

st.write(
    "Upload a Python file, PDF, or text file "
    "and ask Gemini to inspect it."
)


# --------------------------------
# File uploader
# --------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload your file",
    type=[
        "py",
        "pdf",
        "txt"
    ]
)


# --------------------------------
# User question
# --------------------------------
question = st.text_area(
    "💬 What should Gemini inspect?",
    placeholder=(
        "Example: Find bugs in this code "
        "and explain how to fix them."
    )
)


# --------------------------------
# Analyze button
# --------------------------------
if st.button("🔍 Analyze File"):

    if uploaded_file is None:

        st.warning(
            "Please upload a file first."
        )

    elif question.strip() == "":

        st.warning(
            "Please enter what you want Gemini "
            "to analyze."
        )

    else:

        try:

            # --------------------------------
            # Read uploaded file
            # --------------------------------
            file_bytes = uploaded_file.getvalue()


            # --------------------------------
            # Determine MIME type
            # --------------------------------
            if uploaded_file.name.endswith(".py"):

                mime_type = "text/x-python"

            elif uploaded_file.name.endswith(".txt"):

                mime_type = "text/plain"

            elif uploaded_file.name.endswith(".pdf"):

                mime_type = "application/pdf"

            else:

                mime_type = "application/octet-stream"


            # --------------------------------
            # Create Gemini file part
            # --------------------------------
            file_bytes = uploaded_file.getvalue()

            if uploaded_file.name.endswith(".py"):
                mime_type = "text/x-python"

            elif uploaded_file.name.endswith(".txt"):
                mime_type = "text/plain"

            elif uploaded_file.name.endswith(".pdf"):
                mime_type = "application/pdf"

            else:
                mime_type = "application/octet-stream"


            file_part = client.files.upload(
                 file=uploaded_file,
                 config={
                     "mime_type": mime_type
                 }
)

            


            # --------------------------------
            # Create prompt
            # --------------------------------
            prompt = f"""
You are an expert code and document inspector.

The user uploaded this file:

{uploaded_file.name}

The user wants you to:

{question}

Analyze the uploaded file carefully.

If it is Python code:

- Identify bugs
- Identify syntax errors
- Identify logical problems
- Explain the problems clearly
- Suggest fixes
- Mention the relevant code section when possible

If it is a document:

- Summarize the important information
- Identify important sections
- Answer the user's question
- Explain the information clearly

Do not invent information that is not present
in the uploaded file.
"""


            # --------------------------------
            # Send file + prompt to Gemini
            # --------------------------------
            with st.spinner(
                "Gemini is inspecting your file..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=[
                        file_part,
                        prompt
                    ]
                )


            # --------------------------------
            # Display result
            # --------------------------------
            st.subheader(
                "🤖 Gemini's Analysis"
            )

            st.write(
                response.text
            )


        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )