import os
import re

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


# -----------------------------
# Load OpenAI API key
# -----------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key was not found. Check your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)


# -----------------------------
# Page setup
# -----------------------------

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


# -----------------------------
# Upload PDF
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload a Financial Report",
    type=["pdf"]
)


if uploaded_file is not None:

    reader = PdfReader(uploaded_file)

    st.success("PDF uploaded successfully!")

    st.write(f"Number of pages: {len(reader.pages)}")

    page_texts = []


    # -----------------------------
    # Extract text page by page
    # -----------------------------

    for page in reader.pages:

        text = page.extract_text()

        if text:
            page_texts.append(text)
        else:
            page_texts.append("")


    # -----------------------------
    # Question box
    # -----------------------------

    st.subheader("Ask the AI about this financial report")

    question = st.text_input(
        "Enter your question:"
    )


    if st.button("Analyze Report"):

        if not question:

            st.warning("Please enter a question first.")

        else:

            # -----------------------------
            # Find relevant pages
            # -----------------------------

            stop_words = {
                "the", "a", "an", "and", "or", "of", "to",
                "in", "on", "for", "with", "what", "were",
                "was", "is", "are", "how", "did", "they",
                "their", "compared", "about"
            }

            question_words = re.findall(
                r"[a-zA-Z0-9]+",
                question.lower()
            )

            keywords = [
                word for word in question_words
                if word not in stop_words and len(word) > 1
            ]


            def score_page(text):

                text_lower = text.lower()

                score = 0

                for keyword in keywords:
                    score += text_lower.count(keyword)

                # Give extra weight to important finance phrases
                finance_phrases = [
                    "net sales",
                    "net income",
                    "revenue",
                    "operating income",
                    "cash flow",
                    "total assets",
                    "gross margin",
                    "earnings per share"
                ]

                for phrase in finance_phrases:

                    if phrase in question.lower() and phrase in text_lower:
                        score += 20

                return score


            ranked_pages = sorted(
                enumerate(page_texts, start=1),
                key=lambda item: score_page(item[1]),
                reverse=True
            )


            # Send only the 8 most relevant pages
            selected_pages = ranked_pages[:8]

            context = ""

            page_numbers = []

            for page_number, page_text in selected_pages:

                if page_text.strip():

                    page_numbers.append(page_number)

                    context += (
                        f"\n\n--- PAGE {page_number} ---\n\n"
                        f"{page_text}"
                    )


            # -----------------------------
            # Ask OpenAI
            # -----------------------------

            with st.spinner(
                "Finding relevant pages and analyzing the report..."
            ):

                prompt = f"""
You are a professional financial research analyst.

Answer the user's question using ONLY the excerpts from the
financial report provided below.

RULES:

1. Do not invent financial information.
2. If the answer is not supported by the excerpts, clearly say so.
3. Include the important financial numbers.
4. Compare periods when appropriate.
5. Explain what the numbers mean in clear language.
6. Cite the PDF page number supporting important claims.
7. Keep the answer focused on the user's question.

USER QUESTION:

{question}

RELEVANT FINANCIAL REPORT PAGES:

{context}
"""

                try:

                    response = client.responses.create(
                        model="gpt-5.6-luna",
                        input=prompt,
                        max_output_tokens=1500
                    )

                    st.subheader("AI Analysis")

                    st.write(response.output_text)

                    st.caption(
                        "Pages searched by the AI: "
                        + ", ".join(map(str, page_numbers))
                    )

                except Exception as error:

                    st.error(
                        "Something went wrong while contacting the AI."
                    )

                    st.write(error)


    # -----------------------------
    # Optional document preview
    # -----------------------------

    with st.expander("View extracted report text"):

        preview_text = ""

        for page_number, text in enumerate(
            page_texts[:5],
            start=1
        ):

            preview_text += (
                f"\n\n--- PAGE {page_number} ---\n\n{text}"
            )

        st.text_area(
            "Extracted Text",
            preview_text,
            height=400
        )