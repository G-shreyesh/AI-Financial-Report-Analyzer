# 📊 AI Financial Report Analyzer

An AI-powered financial analysis application that analyzes company annual reports and 10-K filings using **semantic search, Retrieval-Augmented Generation (RAG), and large language models**.

The application allows users to upload a financial report and automatically analyze revenue, profitability, cash flows, financial position, risks, and custom finance-related questions.

---

## 🚀 Features

### 📌 Financial Snapshot
Automatically extracts and compares key financial metrics such as:

- Net Sales / Revenue
- Net Income
- Operating Income
- Earnings Per Share
- Operating Cash Flow
- Cash and Cash Equivalents
- Total Assets
- Total Liabilities
- Year-over-Year Changes

### 💰 Revenue Analysis
Analyzes:

- Revenue growth
- Product and service performance
- Year-over-year changes
- Revenue drivers
- Geographic trends
- Management explanations

### 📈 Profitability Analysis
Evaluates:

- Gross Profit
- Gross Margin
- Operating Income
- Operating Margin
- Net Income
- Net Margin
- Earnings Per Share

### 💵 Cash Flow Analysis
Examines:

- Operating Cash Flow
- Investing Activities
- Financing Activities
- Capital Expenditures
- Share Repurchases
- Dividends
- Free Cash Flow indicators
- Working Capital movements

### ⚠️ Risk Analysis
Identifies and summarizes major risks including:

- Business Risk
- Financial Risk
- Market Risk
- Regulatory Risk
- Supply Chain Risk
- Geographic Risk
- Technology Risk
- Competitive Risk

### 💬 Custom Financial Questions
Users can ask their own questions about the uploaded financial report.

Example:

> What were Apple's total net sales in 2025, and how did they change compared with 2024?

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
OpenAI Embeddings
          ↓
Semantic Similarity Search
          ↓
Most Relevant Pages Retrieved
          ↓
Large Language Model Analysis
          ↓
Financial Answer + PDF Page Citations