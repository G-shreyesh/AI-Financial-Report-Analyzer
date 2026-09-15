# 📊 AI Company Document Analyzer

An AI-powered document intelligence application that analyzes company documents using **OpenAI, Retrieval-Augmented Generation (RAG), vector embeddings, and semantic search**.

The application can process multiple business document formats, automatically identify the type of document uploaded, retrieve the most relevant information, and generate context-aware financial and business analysis.

🔗 **Live Application:**  
https://ai-financial-report-analyzer-scyfxsnfu2sgj9lgmfb4ts.streamlit.app/

---

## 🚀 Project Overview

Companies generate large amounts of information across financial reports, spreadsheets, presentations, regulatory filings, earnings materials, operational reports, and other business documents.

Manually reviewing these documents can be time-consuming and makes it difficult to quickly locate the information that matters.

The **AI Company Document Analyzer** was built to make that process faster.

Users can upload a company document and the application will:

1. Extract the document's content
2. Automatically identify the document type
3. Detect company and reporting-period information when available
4. Convert document sections into vector embeddings
5. Use semantic search to retrieve the most relevant information
6. Send retrieved context to an AI model
7. Generate structured financial and business analysis
8. Show the document sections used during retrieval

The system is designed around **Retrieval-Augmented Generation (RAG)** so that analysis is grounded in the uploaded document rather than relying only on the AI model's general knowledge.

---

## 📁 Supported File Types

The application currently supports:

| Format | Supported |
|---|---|
| PDF | ✅ |
| Excel (.xlsx) | ✅ |
| CSV | ✅ |
| Word (.docx) | ✅ |
| PowerPoint (.pptx) | ✅ |
| TXT | ✅ |

This allows the application to analyze many common company documents, including:

- 10-K filings
- 10-Q filings
- Annual reports
- Earnings releases
- Investor presentations
- Financial statements
- Excel financial models
- Budgets
- Forecasts
- Sales reports
- Accounts receivable reports
- Operational reports
- Strategy documents
- Company presentations
- Regulatory filings
- Other text-based business documents

---

## 🧠 Automatic Document Intelligence

After a document is uploaded, the application automatically attempts to identify:

- **Company Name**
- **Document Type**
- **Reporting Period**
- **Fiscal Year**
- **Primary Document Focus**
- **Identification Confidence**

For example, the system can distinguish an investor presentation from a traditional annual report and adjust its analysis accordingly.

Possible document classifications include:

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
- Other Company Document

---

## ⚡ AI Analysis Tools

The application includes several built-in analysis workflows.

### 🏢 Company Overview

Extracts and summarizes information such as:

- Main business activities
- Products and services
- Business segments
- Geographic presence
- Important markets
- Strategic priorities
- Recent developments
- Opportunities
- Challenges

---

### 📌 Financial Snapshot

Attempts to identify important financial metrics including:

- Revenue
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
- Relevant financial ratios

When multiple periods are available, the system can compare financial performance across periods.

---

### 💰 Revenue Analysis

Analyzes:

- Current-period revenue
- Prior-period revenue
- Dollar changes
- Percentage changes
- Segment performance
- Geographic performance
- Product or service trends
- Volume effects
- Pricing effects
- Major revenue drivers

---

### 📈 Profitability Analysis

Examines profitability metrics such as:

- Gross profit
- Gross margin
- Operating income
- Operating margin
- EBITDA when available
- Net income
- Net margin
- Earnings per share
- Expense trends
- Profitability drivers

---

### 💵 Cash Flow Analysis

Analyzes available information related to:

- Operating cash flow
- Capital expenditures
- Investing activities
- Financing activities
- Debt activity
- Dividends
- Share repurchases
- Cash balances
- Liquidity
- Free cash flow when enough information is available

---

### ⚠️ Risk Analysis

Identifies and analyzes risks such as:

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

---

### 📄 Document Summary

Generates an executive-level summary covering the most important information contained in the uploaded document.

Depending on the document, this may include:

- Document purpose
- Important financial figures
- Business developments
- Management commentary
- Opportunities
- Risks
- Trends
- Key conclusions

---

### 💬 Custom Questions

Users are not limited to predefined analyses.

The application includes a custom question interface that allows users to ask questions directly about the uploaded document.

Example questions:

> What were the major drivers of revenue growth?

> What are the company's largest risks?

> How did profitability change compared with the previous period?

> What does management say about future growth?

> Which geographic region generated the most sales?

The semantic retrieval system searches the document for sections most relevant to the question before generating the response.

---

## 🔎 Retrieval-Augmented Generation (RAG)

Instead of sending an entire document directly to the AI model for every question, the application uses a retrieval pipeline.

### RAG Workflow

```text
Company Document
       ↓
Document Extraction
       ↓
Document Identification
       ↓
Text Sections / PDF Pages
       ↓
Vector Embeddings
       ↓
Semantic Search
       ↓
Relevant Sections Retrieved
       ↓
AI Analysis
       ↓
Grounded Response
```

This architecture improves the relevance of the context supplied to the AI model and makes it possible to work with larger company documents more efficiently.

---

## 🧮 Semantic Search

Document sections are converted into vector embeddings using:

```text
text-embedding-3-small
```

When a user selects an analysis or asks a question:

1. The question is converted into an embedding
2. The question embedding is compared with document-section embeddings
3. Cosine similarity is calculated
4. The most relevant sections are selected
5. Those sections become context for the AI analysis

This allows the application to retrieve information based on **meaning**, rather than relying only on exact keyword matching.

---

## 📊 Retrieval Transparency

The application displays information about the semantic retrieval process.

Users can view:

- Retrieved document sections
- Similarity scores
- Semantic retrieval confidence visualization

For PDFs, retrieved information can retain page-level citation labels.

For other supported formats, extracted content is divided into sections that can be referenced during analysis.

This provides greater transparency into which parts of the document were used to generate an answer.

---

## 🗂️ Multi-Format Document Processing

Different document formats require different extraction methods.

The application uses a dedicated document-processing layer to convert supported files into text that can be analyzed by the RAG pipeline.

### PDF

Extracts readable text from individual PDF pages.

### Excel

Reads worksheets and converts tabular information into structured text.

### CSV

Reads structured tabular datasets using Pandas.

### Word

Extracts paragraphs and table content from `.docx` documents.

### PowerPoint

Extracts text from presentation slides.

### TXT

Reads plain-text company documents.

After extraction, the content enters the same semantic-search and AI-analysis pipeline.

---

## 🏗️ Application Architecture

```text
User
  ↓
Streamlit Interface
  ↓
File Upload
  ↓
Document Reader
  ↓
Content Extraction
  ↓
AI Document Classification
  ↓
Document Sections
  ↓
OpenAI Embeddings
  ↓
Vector Similarity Search
  ↓
Relevant Context Retrieval
  ↓
OpenAI Analysis
  ↓
Structured Business / Financial Response
  ↓
Streamlit Dashboard
```

---

## 🛠️ Technology Stack

### Programming

- Python

### Application Framework

- Streamlit

### AI

- OpenAI API

### AI Architecture

- Retrieval-Augmented Generation (RAG)
- Vector Embeddings
- Semantic Search
- Prompt Engineering

### Data Processing

- Pandas
- NumPy

### Document Processing

- PyPDF
- python-docx
- openpyxl
- python-pptx

### Development & Deployment

- Git
- GitHub
- Streamlit Community Cloud

---

## 📂 Project Structure

```text
AI-Financial-Report-Analyzer/
│
├── app.py
├── document_reader.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

### `app.py`

Contains the primary Streamlit application, including:

- User interface
- File upload
- Document processing workflow
- Automatic document identification
- Embedding generation
- Semantic retrieval
- AI analysis
- Retrieval visualization

### `document_reader.py`

Handles extraction from multiple document formats including:

- PDF-related supporting workflow
- Excel
- CSV
- Word
- PowerPoint
- TXT

### `requirements.txt`

Contains the Python dependencies required to run and deploy the application.

---

## 🔐 Environment Variables

The application requires an OpenAI API key.

Create a `.env` file locally:

```text
OPENAI_API_KEY=your_api_key_here
```

The `.env` file should **never be committed to GitHub**.

For cloud deployment, the API key should be stored securely using the deployment platform's secrets-management system.

---

## 💻 Running the Project Locally

Clone the repository:

```bash
git clone <your-repository-url>
```

Navigate to the project directory:

```bash
cd AI-Financial-Report-Analyzer
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
python -m streamlit run app.py
```

The application will normally become available at:

```text
http://localhost:8501
```

---

## 🧪 Testing

The application has been tested with multiple categories of company documents and file formats.

Example test scenarios include:

- Financial filing PDF
- Annual report PDF
- Earnings / investor presentation PDF
- Excel financial dataset
- CSV dataset
- Word business document
- PowerPoint presentation
- Plain-text document

Testing focuses on:

- Successful file extraction
- Document-type identification
- Semantic retrieval
- Financial analysis
- Custom question answering
- Multi-format compatibility

---

## ⚠️ Current Limitations

The project is designed as a portfolio, educational, and research application and has several current limitations.

- Image-only or scanned PDFs may require OCR before their content can be analyzed.
- AI-generated document classification may occasionally be incorrect.
- Financial analysis depends on the information actually contained in the uploaded document.
- Complex spreadsheet formatting, formulas, charts, images, and macros may not be fully represented during text extraction.
- Visual information contained only in images or charts may not be captured.
- Very large documents may require additional optimization or batching.
- Non-PDF citations currently use extracted section references rather than native spreadsheet-cell, Word-paragraph, or PowerPoint-slide citations in all cases.
- AI output should be independently verified before being used for financial or business decisions.

---

## 🔮 Future Improvements

Potential future enhancements include:

- Multi-document analysis
- Company-level knowledge bases
- Comparison of multiple companies
- Quarter-over-quarter comparison
- Automated financial ratio calculation
- Financial statement normalization
- Native Excel sheet/cell citations
- Native PowerPoint slide citations
- Improved document metadata extraction
- OCR for scanned documents
- Chart and image understanding
- Conversation history
- Persistent vector databases
- Document libraries
- Advanced financial dashboards
- Exportable PDF analysis reports

---

## 🎯 Project Goal

The goal of this project is to demonstrate how modern AI systems can combine:

**Financial analysis + document intelligence + semantic retrieval + generative AI**

to transform unstructured and semi-structured company documents into useful business insights.

The project demonstrates practical experience with:

- Financial analysis
- Python development
- OpenAI APIs
- Retrieval-Augmented Generation
- Vector embeddings
- Semantic search
- Multi-format document processing
- AI prompt design
- Streamlit application development
- Git/GitHub workflows
- Cloud deployment

---

## 👨‍💻 Author

**Shreyesh Gaddamwar**

Master's in Quantitative Finance  
University of Massachusetts Dartmouth

---

## ⚖️ Disclaimer

This project is intended for **educational, research, and portfolio purposes only**.

AI-generated outputs may contain errors or omissions and should be independently verified.

Nothing produced by this application should be considered financial, investment, legal, accounting, or professional advice.