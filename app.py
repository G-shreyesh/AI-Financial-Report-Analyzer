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
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Financial Report Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Financial Report Analyzer")

st.write(
    "Upload a company's annual report or 10-K and perform "
    "AI-powered financial analysis using semantic search."
)


# --------------------------------------------------
# Extract PDF pages
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
# Create page embeddings
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def create_page_embeddings(page_texts):

    cleaned_texts = []

    for text in page_texts:

        if text.strip():
            cleaned_texts.append(text[:12000])
        else:
            cleaned_texts.append("Blank page")

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=cleaned_texts
    )

    return [
        item.embedding
        for item in response.data
    ]


# --------------------------------------------------
# Semantic retrieval
# --------------------------------------------------

def find_relevant_pages(
    question,
    pages,
    page_embeddings,
    top_k=10
):

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

    question_norm = np.linalg.norm(
        question_embedding
    )

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
# Analyze retrieved pages
# --------------------------------------------------

def analyze_financial_report(
    question,
    analysis_name,
    pages,
    page_embeddings
):

    relevant_pages = find_relevant_pages(
        question,
        pages,
        page_embeddings,
        top_k=10
    )

    context = ""

    selected_page_numbers = []

    for result in relevant_pages:

        page_number = result["page_number"]

        selected_page_numbers.append(page_number)

        context += (
            f"\n\n--- PDF PAGE {page_number} ---\n\n"
            f"{result['text']}"
        )

    prompt = f"""
You are a professional equity research and financial analysis assistant.

You are analyzing excerpts retrieved from a company's annual
report or Form 10-K.

ANALYSIS TYPE:
{analysis_name}

USER REQUEST:
{question}

Use ONLY the report excerpts supplied below.

FINANCIAL ANALYSIS RULES:

1. Never invent or estimate a number that is not supported
   by the supplied report excerpts.

2. Clearly distinguish between:
   - millions
   - billions
   - percentages
   - per-share amounts

3. Always include a space between a financial number and its unit.
   Example: $416.2 billion, not $416.2billion.

4. Compare the latest year with prior years whenever the
   necessary information is available.

5. Calculate percentage changes only when the underlying
   values are available.

6. Explain significant increases or decreases.

7. Identify important business drivers mentioned in the report.

8. Cite important claims using:
   (PDF p. X)

9. If information cannot be found in the retrieved excerpts,
   explicitly say that the information was not available.

10. Provide interpretation from a finance perspective, but do
    not provide investment advice.

11. Keep the response structured and easy to read.

12. Use clean Markdown headings and bullet points.

13. Do not produce broken Markdown formatting.

REPORT EXCERPTS:

{context}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
        max_output_tokens=1800
    )

    return (
        response.output_text,
        relevant_pages,
        selected_page_numbers
    )


# --------------------------------------------------
# Upload report
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a Financial Report",
    type=["pdf"]
)


if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()

    pages = extract_pdf_pages(
        file_bytes
    )

    st.success(
        "Financial report uploaded successfully!"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Pages in Report",
            len(pages)
        )

    with col2:
        st.metric(
            "Analysis Engine",
            "Semantic RAG"
        )


    # --------------------------------------------------
    # Create semantic index
    # --------------------------------------------------

    page_texts = [
        page["text"]
        for page in pages
    ]

    with st.spinner(
        "Preparing financial report for semantic search..."
    ):

        page_embeddings = create_page_embeddings(
            page_texts
        )


    st.divider()


    # --------------------------------------------------
    # Quick finance analysis
    # --------------------------------------------------

    st.subheader("⚡ Quick Financial Analysis")

    st.write(
        "Choose an analysis below or ask your own question."
    )

    button1, button2, button3 = st.columns(3)

    button4, button5 = st.columns(2)


    analysis_question = None
    analysis_name = None


    with button1:

        if st.button(
            "📌 Financial Snapshot",
            use_container_width=True
        ):

            analysis_name = "Financial Snapshot"

            analysis_question = """
Provide a financial snapshot of the company.

Find the company's consolidated financial statements,
including the income statement, balance sheet, and cash flow
statement.

Identify the most recent available figures for:

- Revenue or net sales
- Net income
- Operating income
- Earnings per share
- Operating cash flow
- Cash and cash equivalents
- Total assets
- Total liabilities

Compare each figure with the prior year where possible.

Pay special attention to pages containing:
- Consolidated Statements of Operations
- Consolidated Balance Sheets
- Consolidated Statements of Cash Flows

Highlight the most important year-over-year changes and explain
what they suggest about the company's financial performance.
"""


    with button2:

        if st.button(
            "💰 Revenue Analysis",
            use_container_width=True
        ):

            analysis_name = "Revenue Analysis"

            analysis_question = """
Analyze the company's revenue or net sales performance.

Include:

- Current-year revenue
- Prior-year revenue
- Dollar change
- Percentage change
- Major products, services, or segments driving revenue
- Geographic trends if available
- Management explanations for major changes

Conclude with a brief interpretation of the revenue trend.
"""


    with button3:

        if st.button(
            "📈 Profitability Analysis",
            use_container_width=True
        ):

            analysis_name = "Profitability Analysis"

            analysis_question = """
Analyze the company's profitability.

Look for:

- Gross profit or gross margin
- Operating income
- Operating margin
- Net income
- Net margin
- Earnings per share

Compare the latest year with the prior year where possible.

Explain the major drivers of profitability changes.
"""


    with button4:

        if st.button(
            "💵 Cash Flow Analysis",
            use_container_width=True
        ):

            analysis_name = "Cash Flow Analysis"

            analysis_question = """
Analyze the company's cash flow position.

Focus on:

- Cash flow from operating activities
- Capital expenditures
- Investing activities
- Financing activities
- Share repurchases
- Dividends
- Cash balance

If enough information exists, discuss approximate free cash
flow using operating cash flow minus capital expenditures.

Explain what the cash flow profile suggests about the company.
"""


    with button5:

        if st.button(
            "⚠️ Risk Analysis",
            use_container_width=True
        ):

            analysis_name = "Risk Analysis"

            analysis_question = """
Identify and analyze the most important risks disclosed in
the company's annual report.

Group risks into useful categories such as:

- Business risk
- Financial risk
- Market risk
- Regulatory risk
- Supply-chain risk
- Geographic risk
- Technology risk
- Competitive risk

Explain which risks appear most significant based on the report.
"""


    # --------------------------------------------------
    # Custom question
    # --------------------------------------------------

    st.divider()

    st.subheader("💬 Ask Your Own Question")

    custom_question = st.text_input(
        "Enter a financial question about the report:"
    )

    if st.button(
        "Analyze Custom Question"
    ):

        if custom_question.strip():

            analysis_name = "Custom Financial Analysis"

            analysis_question = custom_question

        else:

            st.warning(
                "Please enter a question first."
            )


    # --------------------------------------------------
    # Run selected analysis
    # --------------------------------------------------

    if analysis_question:

        try:

            with st.spinner(
                "Retrieving relevant sections and performing "
                "financial analysis..."
            ):

                (
                    answer,
                    relevant_pages,
                    selected_page_numbers
                ) = analyze_financial_report(
                    analysis_question,
                    analysis_name,
                    pages,
                    page_embeddings
                )


            st.divider()

            st.subheader(
                f"📊 {analysis_name}"
            )

            # Escape dollar signs so Streamlit does not
            # interpret financial values as LaTeX math.
            clean_answer = answer.replace("$", r"\$")

            st.markdown(
                clean_answer
            )


            st.caption(
                "Semantically retrieved PDF pages: "
                + ", ".join(
                    map(
                        str,
                        selected_page_numbers
                    )
                )
            )


            # --------------------------------------------------
            # Retrieval details
            # --------------------------------------------------

            with st.expander(
                "🔍 View semantic retrieval details"
            ):

                for result in relevant_pages:

                    st.write(
                        f"PDF Page "
                        f"{result['page_number']} "
                        f"— Similarity Score: "
                        f"{result['similarity']:.3f}"
                    )


        except Exception as error:

            st.error(
                "Something went wrong while analyzing "
                "the financial report."
            )

            st.write(
                error
            )


    # --------------------------------------------------
    # Document preview
    # --------------------------------------------------

    st.divider()

    with st.expander(
        "📄 View extracted report text"
    ):

        preview_text = ""

        for page in pages[:5]:

            preview_text += (
                f"\n\n--- PDF PAGE "
                f"{page['page_number']} ---\n\n"
                f"{page['text']}"
            )

        st.text_area(
            "Extracted Report Text",
            preview_text,
            height=400
        )