import streamlit as st
from google import genai
from PIL import Image

st.title("Visual AI Vision Inspector & OCR Agent")

# Upload image
uploaded_file = st.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg"]
)

# Select mode
mode = st.selectbox(
    "Choose extraction mode",
    [
        "Extract Bill Items as Table",
        "Explain Architecture Diagram",
        "Handwriting OCR"
    ]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Image")

    # Analyze button
    if st.button("Analyze Image"):

        try:
            # Get API key
            api_key = st.secrets["GEMINI_API_KEY"]

            # Create Gemini client
            client = genai.Client(api_key=api_key)

            # Choose prompt
            if mode == "Extract Bill Items as Table":

                prompt = """
                Analyze this receipt carefully.

                Extract all visible bill items.

                Return the result in this format:

                | Item | Quantity | Price |
                |---|---:|---:|

                Also provide:
                - Subtotal
                - Tax
                - Total

                Do not guess information that is not visible.
                """

            elif mode == "Explain Architecture Diagram":

                prompt = """
                Analyze this architecture diagram.

                Explain:
                1. Main components
                2. What each component does
                3. How the components are connected
                4. Overall system flow
                5. where the architecture is located 
                6. why it is famous, who built it, history of it 
                """

            else:

                prompt = """
                Read all handwritten text visible in this image.

                Return the text as accurately as possible.

                If something cannot be read, write [unclear].
                """

            # Send image to Gemini
            with st.spinner("Gemini is analyzing the image... please wait"):

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[prompt, image]
                )

            # Store result
            st.session_state["image"] = image
            st.session_state["client"] = client
            st.session_state["analysis"] = response.text

        except Exception as e:

            st.error("Gemini Error")
            st.write(e)


# Show result if analysis was completed
if "analysis" in st.session_state:

    st.subheader("📊 AI Result")

    st.markdown(st.session_state["analysis"])

    st.divider()

    st.subheader("💬 Ask a Question About This Image")

    question = st.text_input(
        "Ask anything about the uploaded image",
        placeholder="Ask anything 😊?"
    )

    if st.button("Ask"):

        if question:

            try:

                client = st.session_state["client"]
                image = st.session_state["image"]

                with st.spinner("Thinking..."):

                    answer = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[
                            image,
                            question
                        ]
                    )

                st.subheader("🤖 AI Answer")

                st.write(answer.text)

            except Exception as e:

                st.error("Question Error")
                st.write(e)

        else:

            st.warning("Please enter a question.")