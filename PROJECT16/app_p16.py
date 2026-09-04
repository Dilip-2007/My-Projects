import streamlit as st
from google import genai
from dotenv import load_dotenv
from pypdf import PdfReader
import os
import re


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="RAG Knowledge Base Agent",
    page_icon="📚",
    layout="centered"
)


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("📚 In-Memory RAG Knowledge Base Agent")

st.write(
    "Upload policy documents and ask questions. "
    "Gemini will answer using the retrieved document content."
)


# --------------------------------------------------
# Check API key
# --------------------------------------------------

if not api_key:
    st.error("GEMINI_API_KEY is missing from .env")
    st.stop()


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# Extract text from uploaded file
# --------------------------------------------------

def extract_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    # ----------------------------------------------
    # PDF
    # ----------------------------------------------

    if file_name.endswith(".pdf"):

        reader = PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text


    # ----------------------------------------------
    # TXT
    # ----------------------------------------------

    elif file_name.endswith(".txt"):

        return uploaded_file.getvalue().decode(
            "utf-8",
            errors="ignore"
        )


    else:

        return ""


# --------------------------------------------------
# Split document into chunks
# --------------------------------------------------

def create_chunks(text, chunk_size=700):

    # Clean unnecessary spaces
    text = re.sub(r"\s+", " ", text).strip()

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end


    return chunks


# --------------------------------------------------
# Retrieve relevant chunks
# --------------------------------------------------

def retrieve_chunks(query, chunks, top_k=4):
    query_words = set(query.lower().split())

    scored = []

    for chunk in chunks:

        # Handle dictionary chunks
        if isinstance(chunk, dict):
            text = chunk.get("text", "")
        else:
            text = str(chunk)

        words = set(text.lower().split())

        score = len(query_words.intersection(words))

        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [chunk for score, chunk in scored[:top_k]]


    # Return best chunks

    return [
        chunk
        for score, chunk in scored_chunks[:top_k]
        if score > 0
    ]


# --------------------------------------------------
# Upload documents
# --------------------------------------------------

uploaded_files = st.file_uploader(
    "📄 Upload policy documents",
    type=["pdf", "txt"],
    accept_multiple_files=True
)


# --------------------------------------------------
# Process documents
# --------------------------------------------------

all_chunks = []

if uploaded_files:

    for uploaded_file in uploaded_files:

        text = extract_text(uploaded_file)

        if text.strip():

            chunks = create_chunks(text)

            for chunk in chunks:

                all_chunks.append(
                    {
                        "file": uploaded_file.name,
                        "text": chunk
                    }
                )


    st.success(
        f"Loaded {len(uploaded_files)} document(s) "
        f"and created {len(all_chunks)} chunks."
    )


# --------------------------------------------------
# Question
# --------------------------------------------------

question = st.text_area(
    "💬 Ask a question about the documents:",
    placeholder="Example: What is the refund policy?"
)


# --------------------------------------------------
# Ask Gemini
# --------------------------------------------------

if st.button("🔍 Search Knowledge Base"):

    if not uploaded_files:

        st.warning(
            "Please upload at least one document."
        )

        st.stop()


    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()


    # ----------------------------------------------
    # Retrieve relevant chunks
    # ----------------------------------------------

    retrieved = retrieve_chunks(
        question,
        all_chunks,
        top_k=4
    )


    # ----------------------------------------------
    # No relevant information
    # ----------------------------------------------

    if not retrieved:

        st.warning(
            "No relevant information was found "
            "in the knowledge base."
        )

        st.stop()


    # ----------------------------------------------
    # Display retrieved information
    # ----------------------------------------------

    st.subheader("📌 Retrieved Context")


    context_parts = []

    for i, item in enumerate(retrieved, start=1):

        st.markdown(
            f"**Chunk {i} — {item['file']}**"
        )

        st.caption(item["text"])

        context_parts.append(
            f"""
SOURCE {i}: {item['file']}

{item['text']}
"""
        )


    context_parts = []

for chunk in retrieved:
    if isinstance(chunk, dict):
        context_parts.append(chunk.get("text", ""))
    else:
        context_parts.append(str(chunk))

context = "\n\n".join(context_parts)

    # ----------------------------------------------
    # RAG prompt
    # ----------------------------------------------

     prompt = f"""
You are a strict Knowledge Base assistant.

Answer the user's question ONLY using the
information provided in the retrieved context.

Do NOT use outside knowledge.

If the answer is not present in the retrieved
context, say exactly:

"Not found in knowledge base."

Do not guess or invent information.

User question:

{question}

Retrieved context:

{context}

Instructions:

1. Answer clearly and concisely.
2. Use only the retrieved context.
3. If the information is missing, say:
   "Not found in knowledge base."
4. Mention the source document when possible.
"""


    # ----------------------------------------------
    # Generate answer
    # ----------------------------------------------

    try:

        with st.spinner(
            "Gemini is analyzing the retrieved context..."
        ):

            response = client.models.generate_content(
                model="gemini-3.7-flash",
                contents=prompt
            )


        # ------------------------------------------
        # Final answer
        # ------------------------------------------

        st.subheader("🎯 Answer")

        st.write(response.text)


    except Exception as e:

        st.error(
            f"Something went wrong: {e}"
        )