import io
import os

import numpy as np
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


# --------------------------------------------------
# Load API key
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key was not found. Check your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)


# --------------------------------------------------
# Streamlit page setup
# --------------------------------------------------

st.set_page_config(
    page_title="AI Financial Report Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Financial Report Analyzer")

st.write(
    "Upload a company's annual report or 10-K and ask questions "
    "about its financial performance."
)


# --------------------------------------------------
# Extract PDF text
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def extract_pdf_pages(file_bytes):

    reader = PdfReader(io.BytesIO(file_bytes))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text is None:
            text = ""

        pages.append(
            {
                "page_number": page_number,
                "text": text
            }
        )

    return pages


# --------------------------------------------------
# Create semantic embeddings for report pages
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def create_page_embeddings(page_texts):

    cleaned_texts = []

    for text in page_texts:

        if text.strip():
            # Keep embedding input reasonably sized
            cleaned_texts.append(text[:12000])

        else:
            cleaned_texts.append("Blank page")

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=cleaned_texts
    )

    embeddings = [
        item.embedding
        for item in response.data
    ]

    return embeddings


# --------------------------------------------------
# Find most relevant pages using cosine similarity
# --------------------------------------------------

def find_relevant_pages(question, pages, page_embeddings, top_k=6):

    question_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    question_embedding = np.array(
        question_response.data[0].embedding,
        dtype=np.float32
    )

    document_embeddings = np.array(
        page_embeddings,
        dtype=np.float32
    )

    question_norm = np.linalg.norm(question_embedding)

    document_norms = np.linalg.norm(
        document_embeddings,
        axis=1
    )

    similarities = (
        document_embeddings @ question_embedding
    ) / (
        document_norms * question_norm + 1e-10
    )

    best_indexes = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for index in best_indexes:

        results.append(
            {
                "page_number": pages[index]["page_number"],
                "text": pages[index]["text"],
                "similarity": float(similarities[index])
            }
        )

    return results


# --------------------------------------------------
# File upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a Financial Report",
    type=["pdf"]
)


if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()

    pages = extract_pdf_pages(file_bytes)

    st.success("PDF uploaded successfully!")

    st.write(f"Number of pages: {len(pages)}")


    # --------------------------------------------------
    # Question section
    # --------------------------------------------------

    st.subheader("Ask the AI about this financial report")

    question = st.text_input(
        "Enter your question:"
    )


    if st.button("Analyze Report"):

        if not question:

            st.warning("Please enter a question first.")

        else:

            try:

                # ------------------------------------------
                # Step 1: Create semantic index
                # ------------------------------------------

                with st.spinner(
                    "Building semantic search index..."
                ):

                    page_texts = [
                        page["text"]
                        for page in pages
                    ]

                    page_embeddings = create_page_embeddings(
                        page_texts
                    )


                # ------------------------------------------
                # Step 2: Retrieve relevant pages
                # ------------------------------------------

                with st.spinner(
                    "Finding the most relevant pages..."
                ):

                    relevant_pages = find_relevant_pages(
                        question,
                        pages,
                        page_embeddings,
                        top_k=6
                    )


                # ------------------------------------------
                # Step 3: Build AI context
                # ------------------------------------------

                context = ""

                selected_page_numbers = []

                for result in relevant_pages:

                    page_number = result["page_number"]

                    selected_page_numbers.append(
                        page_number
                    )

                    context += (
                        f"\n\n--- PDF PAGE {page_number} ---\n\n"
                        f"{result['text']}"
                    )


                # ------------------------------------------
                # Step 4: Ask AI
                # ------------------------------------------

                with st.spinner(
                    "Analyzing the financial report..."
                ):

                    prompt = f"""
You are a professional financial research analyst.

The user has uploaded a company's annual report or 10-K.

Answer the user's question using ONLY the financial report
excerpts provided below.

IMPORTANT RULES:

1. Do not invent financial information.
2. If the report excerpts do not contain enough information,
   clearly say that.
3. Include important financial numbers when relevant.
4. Compare financial periods when appropriate.
5. Explain the answer clearly for someone studying finance.
6. Cite the PDF page number supporting important claims.
7. Distinguish between millions, billions, percentages,
   and per-share amounts carefully.
8. If useful, explain what the result may indicate about
   the company's financial performance.
9. Keep the answer focused on the question.

USER QUESTION:

{question}


RELEVANT FINANCIAL REPORT EXCERPTS:

{context}
"""

                    response = client.responses.create(
                        model="gpt-5.6-luna",
                        input=prompt,
                        max_output_tokens=1500
                    )


                # ------------------------------------------
                # Display answer
                # ------------------------------------------

                st.subheader("AI Analysis")

                st.write(response.output_text)

                st.caption(
                    "Semantically retrieved PDF pages: "
                    + ", ".join(
                        map(str, selected_page_numbers)
                    )
                )


                # ------------------------------------------
                # Show retrieval details
                # ------------------------------------------

                with st.expander(
                    "View semantic retrieval details"
                ):

                    for result in relevant_pages:

                        st.write(
                            f"Page {result['page_number']} "
                            f"— Similarity score: "
                            f"{result['similarity']:.3f}"
                        )


            except Exception as error:

                st.error(
                    "Something went wrong while analyzing the report."
                )

                st.write(error)


    # --------------------------------------------------
    # Document preview
    # --------------------------------------------------

    with st.expander("View extracted report text"):

        preview_text = ""

        for page in pages[:5]:

            preview_text += (
                f"\n\n--- PDF PAGE "
                f"{page['page_number']} ---\n\n"
                f"{page['text']}"
            )

        st.text_area(
            "Extracted Text",
            preview_text,
            height=400
        )