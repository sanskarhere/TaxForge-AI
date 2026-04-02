# <mark> <i> TaxForge-AI </i> </mark>

### AI-Powered Synthetic Tax Dataset Generator & Document Automation Engine

---

## 🧠 Overview

**TaxForge AI** is a production-style system designed to generate **high-quality synthetic tax datasets** along with **fully structured PDF documents**.

It simulates real-world tax scenarios by combining:
- realistic user profiles  
- diverse income patterns  
- rule-based tax calculations  
- automated document generation  

The system ensures **data consistency across all forms**, making it ideal for:
- AI/ML training datasets  
- document automation testing  
- financial simulation systems  

---

## 🎯 Problem It Solves

Real tax data is:
- ❌ sensitive (PII issues)  
- ❌ hard to access  
- ❌ legally restricted  

👉 TaxForge AI solves this by generating:

> **Fully synthetic, privacy-safe, yet realistic tax datasets**

---

## ⚙️ What This Project Does

✔ Generates complete synthetic tax cases  
✔ Simulates multiple income sources (W2, 1099, Business)  
✔ Applies Federal & State tax logic  
✔ Produces structured outputs (JSON + Markdown)  
✔ Converts them into professional PDFs  

---

## 🧩 System Architecture

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


## 📂 Output Structure

Each generated case contains:


CASE_0001/
│
├── case_data.json
├── client_summary.pdf
├── prompt.pdf
├── executive_summary.pdf
└── completed_forms_summary.pdf

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
