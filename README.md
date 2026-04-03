# <mark> <i> TaxForge-AI </i> </mark>

### AI-Powered Synthetic Tax Dataset Generator & Document Automation Engine

---

## 🧠 Overview

TaxForge-AI is a production-style system that generates high-quality synthetic tax datasets along with fully structured, IRS-style PDF documents.

It simulates real-world tax scenarios by combining:

realistic taxpayer profiles

multiple income streams (W2, 1099, business income)

rule-based federal & state tax calculations

automated document generation pipelines

👉 The system ensures end-to-end consistency across all outputs, making it suitable for real-world experimentation and testing.

🎯 Problem Statement

Accessing real tax data is challenging due to:

❌ Privacy concerns (PII exposure)

❌ Legal restrictions

❌ Limited availability for ML training

✅ Solution

TaxForge-AI generates:

Fully synthetic, privacy-safe, yet structurally realistic tax datasets

⚙️ Key Features

✔ End-to-end synthetic tax case generation

✔ Supports multiple income types (W2, 1099, Schedule C)

✔ Federal + California tax rule simulation

✔ Structured outputs (JSON + Markdown)

✔ Automated PDF document generation

✔ Conditional form inclusion (e.g., Schedule C, 8812)

✔ Consistent multi-document pipeline

🧩 System Architecture

Synthetic Profile Generator
↓
Income Generator (W2 / 1099 / Schedule C)
↓
Tax Rule Engine (Federal + California)
↓
Template Engine (Jinja2)
↓
Markdown → PDF Renderer (ReportLab)
↓
Final Output (Multi-document dataset)

📂 Output Structure

Each generated case contains:

CASE_0001/
│
├── case_data.json
├── client_summary.pdf
├── executive_summary.pdf
├── prompt.pdf
└── completed_forms_summary.pdf

👉 All files are internally consistent and derived from the same generated case.



## 🚀 How to Run

### 1. Clone repo

git clone https://github.com/your-username/taxforge-ai.git
cd taxforge-ai
### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
### 3. Install dependencies
pip install -r requirements.txt
pip install -e[dev]
