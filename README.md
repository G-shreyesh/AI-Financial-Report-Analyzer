# 📊 AI Financial Report Analyzer

An AI-powered financial research application that analyzes company **10-K filings and annual reports** using **Retrieval-Augmented Generation (RAG), semantic search, vector embeddings, and large language models**.

Users can upload a financial report and instantly perform revenue, profitability, cash flow, financial position, and risk analysis — with supporting PDF page references.

## 🌐 Live Demo

👉 **[Try the AI Financial Report Analyzer](https://ai-financial-report-analyzer-scyfxsnfu2sgj9lgmfb4ts.streamlit.app/)**

---

## 🚀 Key Features

### 📌 Financial Snapshot

Automatically extracts and analyzes key financial metrics, including:

- Revenue / Net Sales
- Operating Income
- Net Income
- Earnings Per Share
- Operating Cash Flow
- Cash and Cash Equivalents
- Total Assets
- Total Liabilities
- Year-over-Year Changes

### 💰 Revenue Analysis

Analyzes:

- Current-year revenue
- Prior-year revenue
- Dollar and percentage changes
- Product and service trends
- Geographic trends
- Major revenue drivers
- Management explanations

### 📈 Profitability Analysis

Evaluates:

- Gross Margin
- Operating Income
- Operating Margin
- Net Income
- Net Margin
- Earnings Per Share
- Year-over-Year Profitability Trends

### 💵 Cash Flow Analysis

Examines:

- Operating Cash Flow
- Capital Expenditures
- Investing Activities
- Financing Activities
- Share Repurchases
- Dividends
- Cash Position
- Free Cash Flow indicators
- Working Capital movements

### ⚠️ Risk Analysis

Identifies and summarizes major company risks, including:

- Business Risk
- Financial Risk
- Market Risk
- Regulatory Risk
- Supply Chain Risk
- Geographic Risk
- Technology Risk
- Competitive Risk

### 💬 Custom Financial Questions

Users can ask their own questions about the uploaded report.

Example:

> What were Apple's total net sales in 2025, and how did they change compared with 2024?

### 🔎 Source Page Retrieval

The application identifies and displays the PDF pages most relevant to each analysis.

### 📊 Semantic Retrieval Visualization

A chart displays the similarity scores of the pages retrieved by the semantic search system.

### ⬇️ Download Analysis

Users can download generated financial analysis results as a text file.

---

## 🧠 How It Works

The application uses a **Retrieval-Augmented Generation (RAG)** architecture.

```text
10-K / Annual Report PDF
          ↓
PDF Text Extraction
          ↓
Page-by-Page Processing
          ↓
Vector Embeddings
          ↓
Semantic Similarity Search
          ↓
Most Relevant Pages Retrieved
          ↓
Large Language Model
          ↓
Financial Analysis
          ↓
Answer + Supporting PDF Pages
```

Instead of sending an entire 10-K to the AI for every request, the application first identifies the sections most relevant to the user's question.

This helps improve:

- Response relevance
- Token efficiency
- Processing speed
- API cost efficiency
- Source traceability

---

## 🔍 Semantic Search

Each page of the uploaded financial report is converted into a numerical vector representation using:

```text
text-embedding-3-small
```

The user's question is also converted into an embedding.

The application then uses **cosine similarity** to compare the question vector with the financial-report page vectors.

The highest-ranking pages are retrieved and supplied to the language model as context.

This allows the application to retrieve information based on **meaning**, rather than relying only on exact keyword matches.

---

## 🏦 Finance-Focused RAG

The application is specifically designed for financial-report analysis.

Its prompts instruct the AI to:

- Use only information retrieved from the uploaded report
- Avoid inventing unsupported financial figures
- Distinguish millions, billions, percentages, and per-share values
- Compare financial periods when data is available
- Calculate year-over-year changes
- Identify important financial drivers
- Provide supporting PDF page references
- Explain financial results in clear language
- Avoid providing investment advice

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **OpenAI API**
- **OpenAI Embeddings**
- **Retrieval-Augmented Generation (RAG)**
- **Semantic Search**
- **Vector Embeddings**
- **Cosine Similarity**
- **NumPy**
- **Pandas**
- **PyPDF**
- **Python-dotenv**
- **Git**
- **GitHub**
- **Streamlit Community Cloud**

---

## 📄 Example Use Cases

Upload a company's annual report or Form 10-K and ask questions such as:

- How much did revenue grow this year?
- What caused the change in profitability?
- How did operating income change?
- What is the company's operating margin?
- How has operating cash flow changed?
- What are total assets and liabilities?
- What products contributed most to revenue growth?
- How has EPS changed year over year?
- What are the company's largest business risks?
- What regulatory risks does management discuss?
- What does the company's cash flow profile indicate?

---

## 📊 Example Analysis

The application was tested using Apple's Form 10-K.

It successfully performed analyses including:

- Financial Snapshot
- Revenue Analysis
- Profitability Analysis
- Cash Flow Analysis
- Risk Analysis
- Custom Financial Questions

The system retrieves relevant report pages before generating each response and displays those pages as supporting sources.

---

## 🔐 API Key Security

The OpenAI API key is **not stored in the source code**.

For local development, it is stored inside a `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
```

The `.env` file is excluded from Git using `.gitignore`.

For the deployed application, the API key is stored securely using **Streamlit Community Cloud Secrets**.

This prevents credentials from being exposed in the public GitHub repository.

---

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/G-shreyesh/AI-Financial-Report-Analyzer.git
```

### 2. Open the project folder

```bash
cd AI-Financial-Report-Analyzer
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Create a `.env` file

Inside the project folder, create:

```text
.env
```

Add:

```text
OPENAI_API_KEY=your_api_key_here
```

### 7. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 📁 Project Structure

```text
AI-Financial-Report-Analyzer/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
└── .env
```

> `.env` exists only in the local development environment and is intentionally excluded from GitHub.

---

## 🎯 Project Objective

The goal of this project is to combine **Artificial Intelligence with Financial Analysis** to create a practical research tool for interpreting complex financial disclosures.

The project demonstrates hands-on experience with:

- Generative AI
- Financial Statement Analysis
- Retrieval-Augmented Generation
- Vector Embeddings
- Semantic Search
- Prompt Engineering
- API Integration
- Financial Data Interpretation
- Python Application Development
- Cloud Deployment
- Git Version Control
- GitHub

---

## 🔮 Future Improvements

Potential future enhancements include:

- Multi-company financial comparison
- Automatic financial ratio calculations
- Historical trend charts
- Revenue and profitability visualization
- Multi-year comparison
- Improved document chunking
- Persistent vector databases
- Conversation history
- Company and ticker recognition
- Automated KPI extraction
- Exportable PDF financial reports
- SEC filing integration
- Financial news integration

---

## ⚠️ Disclaimer

This project is designed for educational, research, and demonstration purposes.

AI-generated analysis may contain errors and should not be considered financial or investment advice.

---

## 👨‍💻 Author

**Shreyesh Gaddamwar**

Master's in Quantitative Finance  
AI × Finance Project Portfolio