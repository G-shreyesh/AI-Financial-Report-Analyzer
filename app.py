import io
import os

import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="AI Financial Report Analyzer",
    page_icon="📊",
    layout="wide",
)

if not api_key:
    st.error("OpenAI API key was not found.")
    st.stop()

client = OpenAI(api_key=api_key)


# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .feature-box {
        padding: 18px;
        border: 1px solid #e6e6e6;
        border-radius: 12px;
        margin-bottom: 10px;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #e8e8e8;
        padding: 15px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="main-title">📊 AI Financial Report Analyzer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Analyze 10-Ks and annual reports using AI, semantic search,
    and Retrieval-Augmented Generation (RAG).
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("About")

    st.write(
        "This application retrieves relevant sections from "
        "financial reports and uses AI to perform finance-focused analysis."
    )

    st.divider()

    st.subheader("Analysis Tools")

    st.write("📌 Financial Snapshot")
    st.write("💰 Revenue Analysis")
    st.write("📈 Profitability Analysis")
    st.write("💵 Cash Flow Analysis")
    st.write("⚠️ Risk Analysis")
    st.write("💬 Custom Questions")

    st.divider()

    st.caption(
        "Built with Python, Streamlit, OpenAI, embeddings, "
        "semantic search, and RAG."
    )


# --------------------------------------------------
# Extract PDF
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
                "text": text,
            }
        )

    return pages


# --------------------------------------------------
# Embeddings
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
        input=cleaned_texts,
    )

    return [
        item.embedding
        for item in response.data
    ]


# --------------------------------------------------
# Semantic search
# --------------------------------------------------

def find_relevant_pages(
    question,
    pages,
    page_embeddings,
    top_k=10,
):

    question_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question,
    )

    question_embedding = np.array(
        question_response.data[0].embedding,
        dtype=np.float32,
    )

    document_embeddings = np.array(
        page_embeddings,
        dtype=np.float32,
    )

    similarities = (
        document_embeddings @ question_embedding
    ) / (
        np.linalg.norm(document_embeddings, axis=1)
        * np.linalg.norm(question_embedding)
        + 1e-10
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
                "similarity": float(similarities[index]),
            }
        )

    return results


# --------------------------------------------------
# AI analysis
# --------------------------------------------------

def analyze_financial_report(
    question,
    analysis_name,
    pages,
    page_embeddings,
):

    relevant_pages = find_relevant_pages(
        question,
        pages,
        page_embeddings,
        top_k=10,
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
You are a professional financial analyst.

ANALYSIS TYPE:
{analysis_name}

USER REQUEST:
{question}

Use ONLY the financial report excerpts below.

RULES:

1. Never invent financial information.
2. Clearly distinguish millions, billions, percentages,
   and per-share amounts.
3. Compare periods when data is available.
4. Calculate percentage changes when possible.
5. Explain important financial drivers.
6. Cite important claims using (PDF p. X).
7. Clearly state when information is unavailable.
8. Provide finance-focused interpretation.
9. Do not provide investment advice.
10. Use clean Markdown headings and bullet points.
11. Always put spaces between numbers and units.
12. Keep the answer professional and concise.

REPORT EXCERPTS:

{context}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
        max_output_tokens=1800,
    )

    return (
        response.output_text,
        relevant_pages,
        selected_page_numbers,
    )


# --------------------------------------------------
# Upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a 10-K or Annual Report",
    type=["pdf"],
)


# --------------------------------------------------
# Before report upload
# --------------------------------------------------

if uploaded_file is None:

    st.info(
        "Upload a PDF financial report to begin."
    )

    st.markdown("### What this application can do")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-box">
            <b>📊 Analyze Financials</b><br><br>
            Revenue, profitability, cash flow, EPS,
            assets, liabilities, and more.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-box">
            <b>🧠 Semantic RAG</b><br><br>
            Retrieves relevant report pages instead of
            sending the entire document.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-box">
            <b>🔎 Source Citations</b><br><br>
            Financial answers include supporting
            PDF page references.
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# After report upload
# --------------------------------------------------

else:

    file_bytes = uploaded_file.getvalue()

    pages = extract_pdf_pages(file_bytes)

    page_texts = [
        page["text"]
        for page in pages
    ]

    st.success(
        f"Loaded: {uploaded_file.name}"
    )

    with st.spinner(
        "Building semantic search index..."
    ):

        page_embeddings = create_page_embeddings(
            page_texts
        )


    # --------------------------------------------------
    # Report dashboard
    # --------------------------------------------------

    st.markdown("## Report Dashboard")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Pages",
            len(pages),
        )

    with metric2:
        st.metric(
            "AI Engine",
            "Semantic RAG",
        )

    with metric3:
        st.metric(
            "Status",
            "Ready",
        )

    st.divider()


    # --------------------------------------------------
    # Analysis buttons
    # --------------------------------------------------

    st.markdown("## ⚡ Quick Financial Analysis")

    st.caption(
        "Select an analysis below or ask a custom question."
    )

    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1, row2_col2 = st.columns(2)

    analysis_name = None
    analysis_question = None


    # Financial Snapshot
    with row1_col1:

        if st.button(
            "📌 Financial Snapshot",
            use_container_width=True,
        ):

            analysis_name = "Financial Snapshot"

            analysis_question = """
Provide a complete financial snapshot.

Find:

- Revenue or net sales
- Net income
- Operating income
- Earnings per share
- Operating cash flow
- Cash and cash equivalents
- Total assets
- Total liabilities

Compare the latest year with the prior year.

Pay particular attention to the company's consolidated
income statement, balance sheet, and cash flow statement.

Highlight the most important year-over-year changes.
"""


    # Revenue Analysis
    with row1_col2:

        if st.button(
            "💰 Revenue Analysis",
            use_container_width=True,
        ):

            analysis_name = "Revenue Analysis"

            analysis_question = """
Analyze revenue performance.

Include:

- Latest-year revenue
- Prior-year revenue
- Dollar change
- Percentage change
- Product or service revenue trends
- Segment trends
- Geographic trends
- Important revenue drivers

Finish with a short finance interpretation.
"""


    # Profitability Analysis
    with row1_col3:

        if st.button(
            "📈 Profitability Analysis",
            use_container_width=True,
        ):

            analysis_name = "Profitability Analysis"

            analysis_question = """
Analyze profitability.

Include:

- Gross margin
- Operating income
- Operating margin
- Net income
- Net margin
- Earnings per share

Compare the latest year with the prior year.

Explain the major reasons profitability changed.
"""


    # Cash Flow Analysis
    with row2_col1:

        if st.button(
            "💵 Cash Flow Analysis",
            use_container_width=True,
        ):

            analysis_name = "Cash Flow Analysis"

            analysis_question = """
Analyze cash flow performance.

Include:

- Operating cash flow
- Capital expenditures
- Investing activities
- Financing activities
- Share repurchases
- Dividends
- Cash balance
- Approximate free cash flow when possible

Explain what the cash flow profile suggests.
"""


    # Risk Analysis
    with row2_col2:

        if st.button(
            "⚠️ Risk Analysis",
            use_container_width=True,
        ):

            analysis_name = "Risk Analysis"

            analysis_question = """
Analyze the company's major risks.

Consider:

- Business risk
- Financial risk
- Market risk
- Regulatory risk
- Supply-chain risk
- Geographic risk
- Technology risk
- Competitive risk

Rank or emphasize the most important risks
based on the report.
"""


    # --------------------------------------------------
    # Custom questions
    # --------------------------------------------------

    st.divider()

    st.markdown("## 💬 Ask Your Own Financial Question")

    custom_question = st.text_input(
        "Question",
        placeholder=(
            "Example: How did operating income change "
            "compared with last year?"
        ),
        label_visibility="collapsed",
    )

    if st.button(
        "Analyze Question",
        use_container_width=True,
    ):

        if custom_question.strip():

            analysis_name = "Custom Financial Analysis"
            analysis_question = custom_question

        else:

            st.warning(
                "Enter a question first."
            )


    # --------------------------------------------------
    # Run analysis
    # --------------------------------------------------

    if analysis_question:

        try:

            with st.spinner(
                "Retrieving relevant sections and analyzing..."
            ):

                (
                    answer,
                    relevant_pages,
                    selected_page_numbers,
                ) = analyze_financial_report(
                    analysis_question,
                    analysis_name,
                    pages,
                    page_embeddings,
                )

            st.divider()

            st.markdown(
                f"## 📊 {analysis_name}"
            )

            clean_answer = answer.replace(
                "$",
                r"\$",
            )

            st.markdown(
                clean_answer
            )

            st.caption(
                "Source pages retrieved: "
                + ", ".join(
                    map(
                        str,
                        selected_page_numbers,
                    )
                )
            )


            # --------------------------------------------------
            # Semantic retrieval chart
            # --------------------------------------------------

            st.markdown(
                "### 🔎 Semantic Retrieval Confidence"
            )

            retrieval_data = pd.DataFrame(
                {
                    "PDF Page": [
                        str(result["page_number"])
                        for result in relevant_pages
                    ],
                    "Similarity Score": [
                        result["similarity"]
                        for result in relevant_pages
                    ],
                }
            )

            st.bar_chart(
                retrieval_data.set_index(
                    "PDF Page"
                )
            )


            # --------------------------------------------------
            # Download analysis
            # --------------------------------------------------

            st.download_button(
                label="⬇️ Download Analysis",
                data=answer,
                file_name=(
                    analysis_name.lower()
                    .replace(" ", "_")
                    + ".txt"
                ),
                mime="text/plain",
            )


            # --------------------------------------------------
            # Retrieval details
            # --------------------------------------------------

            with st.expander(
                "View retrieval details"
            ):

                for result in relevant_pages:

                    st.write(
                        f"PDF Page {result['page_number']} "
                        f"— Similarity Score: "
                        f"{result['similarity']:.3f}"
                    )


        except Exception as error:

            st.error(
                "Something went wrong while analyzing the report."
            )

            st.write(error)


    # --------------------------------------------------
    # PDF preview
    # --------------------------------------------------

    st.divider()

    with st.expander(
        "📄 View Extracted Report Text"
    ):

        preview_text = ""

        for page in pages[:5]:

            preview_text += (
                f"\n\n--- PDF PAGE "
                f"{page['page_number']} ---\n\n"
                f"{page['text']}"
            )

        st.text_area(
            "Extracted report text",
            preview_text,
            height=400,
        )


# --------------------------------------------------
# Project Highlights
# --------------------------------------------------

st.divider()

st.markdown("### 🚀 Project Highlights")

highlight1, highlight2, highlight3 = st.columns(3)

with highlight1:
    st.metric(
        "Architecture",
        "RAG"
    )

with highlight2:
    st.metric(
        "Retrieval",
        "Semantic Search"
    )

with highlight3:
    st.metric(
        "Deployment",
        "Streamlit Cloud"
    )

st.caption(
    "Built with Python, OpenAI, vector embeddings, semantic search, "
    "financial analysis, GitHub, and Streamlit."
)

st.caption(
    "For educational and research purposes only. "
    "AI-generated analysis should not be considered investment advice."
)