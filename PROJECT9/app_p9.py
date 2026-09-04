import streamlit as st
from google import genai
from google.genai import types
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
    page_title="Live Web Research Agent",
    page_icon="🌐",
    layout="centered"
)


# --------------------------------
# Get API key
# --------------------------------
api_key = os.getenv("GEMINI_API_KEY")


# --------------------------------
# Check API key
# --------------------------------
if not api_key:

    st.error(
        "Gemini API key is missing. "
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
st.title("🌐 Live Web Research Agent")

st.write(
    "Ask a question and Gemini will use Google Search "
    "to find current information from the web."
)


# --------------------------------
# User question
# --------------------------------
question = st.text_area(
    "🔎 Ask a question:",
    placeholder=(
        "Example: What are the latest developments "
        "in artificial intelligence?"
    )
)


# --------------------------------
# Search button
# --------------------------------
if st.button("🌐 Search & Answer"):

    if question.strip() == "":

        st.warning(
            "Please enter a question."
        )

    else:

        try:

            # --------------------------------
            # Enable Google Search grounding
            # --------------------------------
            google_search_tool = types.Tool(
                google_search=types.GoogleSearch()
            )


            # --------------------------------
            # Generate grounded response
            # --------------------------------
            with st.spinner(
                "Searching the web and generating answer..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=question,
                    config=types.GenerateContentConfig(
                        tools=[
                            google_search_tool
                        ]
                    )
                )


            # --------------------------------
            # Display answer
            # --------------------------------
            st.subheader("🤖 Gemini's Answer")

            st.write(
                response.text
            )


            # --------------------------------
            # Grounding metadata
            # --------------------------------
            if response.candidates:

                candidate = response.candidates[0]

                if candidate.grounding_metadata:

                    metadata = (
                        candidate.grounding_metadata
                    )


                    st.subheader(
                        "🔗 Sources Used"
                    )


                    # --------------------------------
                    # Search entry point
                    # --------------------------------
                    if metadata.search_entry_point:

                        st.write(
                            "Google Search was used "
                            "to ground this response."
                        )


                    # --------------------------------
                    # Grounding chunks
                    # --------------------------------
                    if metadata.grounding_chunks:

                        for index, chunk in enumerate(
                            metadata.grounding_chunks,
                            start=1
                        ):

                            if chunk.web:

                                title = (
                                    chunk.web.title
                                    or "Web Source"
                                )

                                uri = chunk.web.uri


                                st.markdown(
                                    f"{index}. "
                                    f"[{title}]({uri})"
                                )


        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )