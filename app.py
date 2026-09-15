import io
import json
import os

import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

from document_reader import extract_document_content


# ==========================================================
# CONFIGURATION
# ==========================================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="AI Company Document Analyzer",
    page_icon="📊",
    layout="wide",
)

if not api_key:
    st.error("OpenAI API key was not found.")
    st.stop()

client = OpenAI(api_key=api_key)


# ==========================================================
# CUSTOM STYLING
# ==========================================================

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
        color: #777;
        margin-bottom: 25px;
    }

    .feature-box {
        padding: 18px;
        border: 1px solid #e6e6e6;
        border-radius: 12px;
        margin-bottom: 10px;
        min-height: 140px;
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


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    '<div class="main-title">📊 AI Company Document Analyzer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Upload company documents and automatically analyze financial,
    operational, strategic, and risk information using AI,
    semantic search, and Retrieval-Augmented Generation (RAG).
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("About")

    st.write(
        "This application analyzes many common company documents "
        "using AI, vector embeddings, semantic search, and RAG."
    )

    st.divider()

    st.subheader("Supported Files")

    st.write("📄 PDF")
    st.write("📊 Excel")
    st.write("📑 CSV")
    st.write("📝 Word")
    st.write("📽️ PowerPoint")
    st.write("📃 TXT")

    st.divider()

    st.subheader("Analysis Tools")

    st.write("🏢 Company Overview")
    st.write("📌 Financial Snapshot")
    st.write("💰 Revenue Analysis")
    st.write("📈 Profitability Analysis")
    st.write("💵 Cash Flow Analysis")
    st.write("⚠️ Risk Analysis")
    st.write("📄 Document Summary")
    st.write("💬 Custom Questions")

    st.divider()

    st.caption(
        "Built with Python, Streamlit, OpenAI, "
        "embeddings, semantic search, and RAG."
    )


# ==========================================================
# PDF EXTRACTION
# ==========================================================

@st.cache_data(show_spinner=False)
def extract_pdf_pages(file_bytes):

    reader = PdfReader(io.BytesIO(file_bytes))

    sections = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):

        text = page.extract_text()

        if text is None:
            text = ""

        if text.strip():

            sections.append(
                {
                    "source": f"PDF Page {page_number}",
                    "citation": f"PDF p. {page_number}",
                    "text": text,
                }
            )

    return sections


# ==========================================================
# GENERIC TEXT CHUNKING
# ==========================================================

def create_text_sections(
    text,
    chunk_size=5000,
    overlap=500,
):

    if not text:
        return []

    text = str(text)

    sections = []

    start = 0
    section_number = 1

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():

            sections.append(
                {
                    "source": f"Section {section_number}",
                    "citation": f"Section {section_number}",
                    "text": chunk,
                }
            )

            section_number += 1

        if end >= len(text):
            break

        start = end - overlap

    return sections


# ==========================================================
# DOCUMENT EXTRACTION
# ==========================================================

def process_uploaded_document(uploaded_file):

    filename = uploaded_file.name

    extension = os.path.splitext(
        filename
    )[1].lower()

    # ------------------------------------------------------
    # PDF
    # ------------------------------------------------------

    if extension == ".pdf":

        file_bytes = uploaded_file.getvalue()

        sections = extract_pdf_pages(
            file_bytes
        )

        full_text = "\n\n".join(
            section["text"]
            for section in sections
        )

        return {
            "success": True,
            "filename": filename,
            "extension": extension,
            "sections": sections,
            "full_text": full_text,
            "error": None,
        }

    # ------------------------------------------------------
    # OTHER DOCUMENT TYPES
    # ------------------------------------------------------

    try:

        uploaded_file.seek(0)

        result = extract_document_content(
            uploaded_file
        )

    except Exception as error:

        return {
            "success": False,
            "filename": filename,
            "extension": extension,
            "sections": [],
            "full_text": "",
            "error": str(error),
        }

    if not result["success"]:

        return {
            "success": False,
            "filename": filename,
            "extension": extension,
            "sections": [],
            "full_text": "",
            "error": result["error"],
        }

    full_text = result["content"]

    sections = create_text_sections(
        full_text
    )

    return {
        "success": True,
        "filename": filename,
        "extension": extension,
        "sections": sections,
        "full_text": full_text,
        "error": None,
    }


# ==========================================================
# DOCUMENT IDENTIFICATION
# ==========================================================

@st.cache_data(show_spinner=False)
def identify_document(
    filename,
    document_text,
):

    sample = document_text[:25000]

    prompt = f"""
You are analyzing a document uploaded to a company intelligence system.

FILE NAME:
{filename}

DOCUMENT CONTENT SAMPLE:
{sample}

Identify the document.

Return ONLY valid JSON.

Use this exact structure:

{{
    "company_name": "company name or Unknown",
    "document_type": "document type",
    "reporting_period": "reporting period or Unknown",
    "fiscal_year": "year or Unknown",
    "primary_focus": "Financial, Operational, Strategic, Regulatory, Investor, or General",
    "confidence": "High, Medium, or Low"
}}

Possible document types include, but are not limited to:

- 10-K
- 10-Q
- Annual Report
- Earnings Release
- Investor Presentation
- Financial Statements
- Income Statement
- Balance Sheet
- Cash Flow Statement
- Excel Financial Model
- Budget
- Forecast
- Accounts Receivable Report
- Sales Report
- Operational Report
- Strategy Document
- Regulatory Filing
- Company Presentation
- Company Memo
- Other Company Document

Do not invent information that is not present.
"""

    try:

        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt,
            max_output_tokens=500,
        )

        response_text = (
            response.output_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(
            response_text
        )

        return data

    except Exception:

        return {
            "company_name": "Unknown",
            "document_type": "Company Document",
            "reporting_period": "Unknown",
            "fiscal_year": "Unknown",
            "primary_focus": "General",
            "confidence": "Low",
        }


# ==========================================================
# EMBEDDINGS
# ==========================================================

@st.cache_data(show_spinner=False)
def create_section_embeddings(
    section_texts,
):

    cleaned_texts = []

    for text in section_texts:

        if text.strip():

            cleaned_texts.append(
                text[:12000]
            )

        else:

            cleaned_texts.append(
                "Blank section"
            )

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=cleaned_texts,
    )

    return [
        item.embedding
        for item in response.data
    ]


# ==========================================================
# SEMANTIC SEARCH
# ==========================================================

def find_relevant_sections(
    question,
    sections,
    section_embeddings,
    top_k=8,
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
        section_embeddings,
        dtype=np.float32,
    )

    similarities = (
        document_embeddings
        @ question_embedding
    ) / (
        np.linalg.norm(
            document_embeddings,
            axis=1,
        )
        * np.linalg.norm(
            question_embedding
        )
        + 1e-10
    )

    top_k = min(
        top_k,
        len(sections),
    )

    best_indexes = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for index in best_indexes:

        results.append(
            {
                "source": sections[index]["source"],
                "citation": sections[index]["citation"],
                "text": sections[index]["text"],
                "similarity": float(
                    similarities[index]
                ),
            }
        )

    return results


# ==========================================================
# AI ANALYSIS
# ==========================================================

def analyze_company_document(
    question,
    analysis_name,
    document_profile,
    sections,
    section_embeddings,
):

    relevant_sections = find_relevant_sections(
        question,
        sections,
        section_embeddings,
        top_k=8,
    )

    context = ""

    source_names = []

    for result in relevant_sections:

        source = result["source"]

        citation = result["citation"]

        source_names.append(source)

        context += (
            f"\n\n--- {source} ---\n"
            f"CITATION LABEL: {citation}\n\n"
            f"{result['text']}"
        )

    company_name = document_profile.get(
        "company_name",
        "Unknown",
    )

    document_type = document_profile.get(
        "document_type",
        "Company Document",
    )

    reporting_period = document_profile.get(
        "reporting_period",
        "Unknown",
    )

    prompt = f"""
You are a professional financial and business analyst.

COMPANY:
{company_name}

DOCUMENT TYPE:
{document_type}

REPORTING PERIOD:
{reporting_period}

ANALYSIS TYPE:
{analysis_name}

USER REQUEST:
{question}

Use ONLY the retrieved document excerpts below.

RULES:

1. Never invent numbers, facts, dates, business events,
   financial metrics, or management statements.

2. If information is unavailable, explicitly say so.

3. Distinguish facts reported in the document from your analysis.

4. Preserve units carefully:
   dollars, thousands, millions, billions,
   percentages, per-share values, etc.

5. Compare periods only when the document provides
   comparable information.

6. Calculate percentage changes only when enough
   information is available.

7. Explain meaningful financial or business drivers.

8. Cite important claims using the exact CITATION LABEL
   supplied with the excerpt.

9. For PDF documents citations may look like:
   (PDF p. 15)

10. For non-PDF documents citations may look like:
    (Section 4)

11. Do not claim that missing information exists.

12. Do not provide investment advice.

13. Use clean Markdown headings and bullet points.

14. Keep the answer professional and easy to understand.

15. Focus the analysis on the type of document uploaded.
    Do not treat every document as a 10-K.

DOCUMENT EXCERPTS:

{context}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
        max_output_tokens=2200,
    )

    return (
        response.output_text,
        relevant_sections,
        source_names,
    )


# ==========================================================
# FILE UPLOAD
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload a Company Document",
    type=[
        "pdf",
        "xlsx",
        "csv",
        "docx",
        "pptx",
        "txt",
    ],
    help=(
        "Supported formats: PDF, Excel (.xlsx), "
        "CSV, Word (.docx), PowerPoint (.pptx), and TXT."
    ),
)


# ==========================================================
# BEFORE FILE UPLOAD
# ==========================================================

if uploaded_file is None:

    st.info(
        "Upload a company document to begin."
    )

    st.markdown(
        "### What this application can analyze"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="feature-box">
            <b>📊 Financial Documents</b><br><br>
            10-Ks, 10-Qs, annual reports, financial statements,
            earnings releases, Excel models, budgets, and forecasts.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="feature-box">
            <b>🏢 Company Documents</b><br><br>
            Investor presentations, operational reports,
            strategy documents, sales reports, company presentations,
            and other business materials.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            """
            <div class="feature-box">
            <b>🧠 Intelligent Analysis</b><br><br>
            Automatically identifies the document, retrieves
            relevant information, and performs context-aware analysis.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================================
# AFTER FILE UPLOAD
# ==========================================================

else:

    with st.spinner(
        "Reading document..."
    ):

        document = process_uploaded_document(
            uploaded_file
        )

    if not document["success"]:

        st.error(
            "The document could not be processed."
        )

        st.write(
            document["error"]
        )

        st.stop()

    sections = document["sections"]

    full_text = document["full_text"]

    if not sections:

        st.error(
            "No readable content was found in this document."
        )

        st.stop()

    st.success(
        f"Loaded: {uploaded_file.name}"
    )


    # ======================================================
    # DOCUMENT IDENTIFICATION
    # ======================================================

    with st.spinner(
        "Identifying document..."
    ):

        document_profile = identify_document(
            uploaded_file.name,
            full_text,
        )


    # ======================================================
    # SEMANTIC INDEX
    # ======================================================

    section_texts = [
        section["text"]
        for section in sections
    ]

    with st.spinner(
        "Building semantic search index..."
    ):

        section_embeddings = create_section_embeddings(
            section_texts
        )


    # ======================================================
    # DOCUMENT DASHBOARD
    # ======================================================

    st.markdown(
        "## 🧠 Document Intelligence"
    )

    metric1, metric2, metric3, metric4 = st.columns(
        4
    )

    with metric1:

        st.metric(
            "Company",
            document_profile.get(
                "company_name",
                "Unknown",
            ),
        )

    with metric2:

        st.metric(
            "Document Type",
            document_profile.get(
                "document_type",
                "Unknown",
            ),
        )

    with metric3:

        period = document_profile.get(
            "reporting_period",
            "Unknown",
        )

        if period == "Unknown":

            period = document_profile.get(
                "fiscal_year",
                "Unknown",
            )

        st.metric(
            "Reporting Period",
            period,
        )

    with metric4:

        st.metric(
            "Identification Confidence",
            document_profile.get(
                "confidence",
                "Unknown",
            ),
        )

    st.caption(
        "Primary focus detected: "
        + document_profile.get(
            "primary_focus",
            "General",
        )
    )

    st.divider()


    # ======================================================
    # ANALYSIS BUTTONS
    # ======================================================

    st.markdown(
        "## ⚡ AI Analysis"
    )

    st.caption(
        "Choose an analysis or ask your own question."
    )

    row1_col1, row1_col2, row1_col3 = st.columns(
        3
    )

    row2_col1, row2_col2, row2_col3 = st.columns(
        3
    )

    analysis_name = None

    analysis_question = None


    # ------------------------------------------------------
    # COMPANY OVERVIEW
    # ------------------------------------------------------

    with row1_col1:

        if st.button(
            "🏢 Company Overview",
            use_container_width=True,
        ):

            analysis_name = (
                "Company Overview"
            )

            analysis_question = """
Provide an executive overview of the company based only
on this document.

Identify when available:

- Main business
- Products or services
- Major business segments
- Geographic presence
- Important customers or markets
- Current priorities
- Major recent developments
- Important financial information
- Main opportunities
- Main challenges

Conclude with the most important takeaways from the document.
"""


    # ------------------------------------------------------
    # FINANCIAL SNAPSHOT
    # ------------------------------------------------------

    with row1_col2:

        if st.button(
            "📌 Financial Snapshot",
            use_container_width=True,
        ):

            analysis_name = (
                "Financial Snapshot"
            )

            analysis_question = """
Provide a financial snapshot using only information
available in this document.

Look for:

- Revenue or net sales
- Gross profit
- Operating income
- Net income
- Earnings per share
- Operating cash flow
- Cash and cash equivalents
- Total assets
- Total liabilities
- Debt
- Equity
- Important financial ratios

Compare periods when possible.

If a metric is not available, explicitly say it was
not found rather than estimating it.
"""


    # ------------------------------------------------------
    # REVENUE
    # ------------------------------------------------------

    with row1_col3:

        if st.button(
            "💰 Revenue Analysis",
            use_container_width=True,
        ):

            analysis_name = (
                "Revenue Analysis"
            )

            analysis_question = """
Analyze revenue or sales performance.

When available include:

- Current-period revenue
- Prior-period revenue
- Dollar change
- Percentage change
- Product or service revenue
- Segment trends
- Geographic trends
- Customer trends
- Volume and pricing effects
- Major revenue drivers
- Management explanations

Finish with a concise business interpretation.

Do not invent revenue figures if this document does
not contain them.
"""


    # ------------------------------------------------------
    # PROFITABILITY
    # ------------------------------------------------------

    with row2_col1:

        if st.button(
            "📈 Profitability Analysis",
            use_container_width=True,
        ):

            analysis_name = (
                "Profitability Analysis"
            )

            analysis_question = """
Analyze profitability using information available
in the document.

When available include:

- Gross profit
- Gross margin
- Operating income
- Operating margin
- EBITDA
- Net income
- Net margin
- Earnings per share
- Expense trends
- Major profitability drivers

Compare available periods.

Explain why profitability improved or deteriorated
when the document provides enough evidence.
"""


    # ------------------------------------------------------
    # CASH FLOW
    # ------------------------------------------------------

    with row2_col2:

        if st.button(
            "💵 Cash Flow Analysis",
            use_container_width=True,
        ):

            analysis_name = (
                "Cash Flow Analysis"
            )

            analysis_question = """
Analyze cash flow and liquidity.

When available include:

- Operating cash flow
- Capital expenditures
- Investing activities
- Financing activities
- Debt activity
- Share repurchases
- Dividends
- Cash balance
- Free cash flow
- Liquidity position

Explain what the cash flow information suggests
about the company.

If cash flow information is not contained in this
document, clearly say so.
"""


    # ------------------------------------------------------
    # RISK
    # ------------------------------------------------------

    with row2_col3:

        if st.button(
            "⚠️ Risk Analysis",
            use_container_width=True,
        ):

            analysis_name = (
                "Risk Analysis"
            )

            analysis_question = """
Identify and analyze the most important risks
described or implied by this document.

Consider when relevant:

- Business risk
- Financial risk
- Liquidity risk
- Competitive risk
- Market risk
- Regulatory risk
- Supply-chain risk
- Customer concentration
- Geographic risk
- Technology risk
- Cybersecurity risk
- Operational risk
- Macroeconomic risk

Rank the most material risks when enough evidence exists.

Separate facts stated in the document from your analysis.
"""


    # ======================================================
    # DOCUMENT SUMMARY
    # ======================================================

    st.divider()

    if st.button(
        "📄 Summarize Entire Document",
        use_container_width=True,
    ):

        analysis_name = (
            "Document Summary"
        )

        analysis_question = """
Provide an executive summary of this document.

Explain:

- What this document is
- Its main purpose
- Most important information
- Important financial figures
- Major business developments
- Management commentary
- Opportunities
- Risks
- Important trends
- Key conclusions

Prioritize information that would be useful to a
financial analyst or business decision-maker.

Do not invent anything missing from the document.
"""


    # ======================================================
    # CUSTOM QUESTION
    # ======================================================

    st.divider()

    st.markdown(
        "## 💬 Ask Your Own Question"
    )

    custom_question = st.text_input(
        "Question",
        placeholder=(
            "Example: What are the biggest changes "
            "reported in this document?"
        ),
        label_visibility="collapsed",
    )

    if st.button(
        "Analyze Question",
        use_container_width=True,
    ):

        if custom_question.strip():

            analysis_name = (
                "Custom Document Analysis"
            )

            analysis_question = (
                custom_question
            )

        else:

            st.warning(
                "Enter a question first."
            )


    # ======================================================
    # RUN ANALYSIS
    # ======================================================

    if analysis_question:

        try:

            with st.spinner(
                "Retrieving relevant information and analyzing..."
            ):

                (
                    answer,
                    relevant_sections,
                    source_names,
                ) = analyze_company_document(
                    analysis_question,
                    analysis_name,
                    document_profile,
                    sections,
                    section_embeddings,
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


            # ==================================================
            # RETRIEVED SOURCES
            # ==================================================

            st.caption(
                "Sources retrieved: "
                + ", ".join(
                    source_names
                )
            )


            # ==================================================
            # SEMANTIC RETRIEVAL CHART
            # ==================================================

            st.markdown(
                "### 🔎 Semantic Retrieval Confidence"
            )

            retrieval_data = pd.DataFrame(
                {
                    "Source": [
                        result["source"]
                        for result in relevant_sections
                    ],
                    "Similarity Score": [
                        result["similarity"]
                        for result in relevant_sections
                    ],
                }
            )

            st.bar_chart(
                retrieval_data.set_index(
                    "Source"
                )
            )


            # ==================================================
            # DOWNLOAD ANALYSIS
            # ==================================================

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


            # ==================================================
            # RETRIEVAL DETAILS
            # ==================================================

            with st.expander(
                "View retrieval details"
            ):

                for result in relevant_sections:

                    st.write(
                        f"{result['source']} "
                        f"— Similarity Score: "
                        f"{result['similarity']:.3f}"
                    )

        except Exception as error:

            st.error(
                "Something went wrong while analyzing the document."
            )

            st.write(
                error
            )


    # ======================================================
    # EXTRACTED CONTENT PREVIEW
    # ======================================================

    st.divider()

    with st.expander(
        "📄 View Extracted Document Content"
    ):

        preview_text = ""

        for section in sections[:5]:

            preview_text += (
                f"\n\n--- {section['source']} ---\n\n"
                f"{section['text']}"
            )

        st.text_area(
            "Extracted document content",
            preview_text,
            height=400,
        )


# ==========================================================
# PROJECT HIGHLIGHTS
# ==========================================================

st.divider()

st.markdown(
    "### 🚀 Project Highlights"
)

highlight1, highlight2, highlight3, highlight4 = st.columns(
    4
)

with highlight1:

    st.metric(
        "Architecture",
        "RAG",
    )

with highlight2:

    st.metric(
        "Retrieval",
        "Semantic Search",
    )

with highlight3:

    st.metric(
        "Documents",
        "Multi-format",
    )

with highlight4:

    st.metric(
        "Deployment",
        "Streamlit Cloud",
    )

st.caption(
    "Built with Python, OpenAI, vector embeddings, "
    "semantic search, document intelligence, RAG, "
    "GitHub, and Streamlit."
)

st.caption(
    "For educational and research purposes only. "
    "AI-generated analysis should not be considered investment advice."
)