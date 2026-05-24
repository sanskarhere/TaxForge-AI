# <mark> <i> TaxForge-AI </i> </mark>

> Privacy-safe synthetic tax data generation and form-ready automation pipeline for document AI testing.

`tax_synth` generates realistic but fully artificial tax records for testing tax automation, document AI, data validation, and form-filling workflows without using real taxpayer information.

---

## The Problem

Tax automation systems need realistic data for testing, but real taxpayer data is private, sensitive, and unsafe to use during development.

Random dummy data is also weak because tax fields are connected. Income, deductions, credits, withholding, taxable income, and form-level values must stay logically consistent.

`tax_synth` solves this by generating synthetic records that are safe, structured, and useful for engineering workflows.

```text
Synthetic Taxpayer → Income Data → Derived Tax Fields → Form Mapping → Validation → Export
```

---

## What This Project Does

- Generates synthetic taxpayer profiles
- Simulates income, deductions, credits, and withholding values
- Maintains logical consistency across related tax fields
- Prepares form-ready structured outputs
- Supports rule-based validation checks
- Exports safe sample datasets for testing
- Uses a modular Python project structure

---

## Example Use Case

A team is building a system that extracts, validates, or fills tax forms automatically.

They cannot use real taxpayer records during development, and random placeholder data does not properly test real-world tax relationships.

`tax_synth` provides synthetic records that behave like realistic tax data while remaining safe for demos, testing, and experimentation.

```text
Profile Generation
        ↓
Income Simulation
        ↓
Deduction & Credit Logic
        ↓
Form Field Mapping
        ↓
Validation Checks
        ↓
Dataset / Form Output
```

---

## Project Structure

```text
tax_synth/
│
├── src/
│   ├── data_generation/      # Taxpayer, income, deduction, and credit generation
│   ├── form_filling/         # Form field mapping and PDF/form output logic
│   ├── validation/           # Consistency and schema validation
│   ├── pipelines/            # End-to-end generation workflows
│   └── utils/                # Shared helpers and config utilities
│
├── configs/                  # Generation rules and form configs
├── schemas/                  # Data schema definitions
├── sample_data/              # Small safe demo datasets
├── sample_outputs/           # Redacted sample outputs
├── tests/                    # Unit tests
├── main.py                   # Pipeline entry point
├── requirements.txt
└── README.md
```

---

## Tech Stack

- Python
- Pandas
- Faker
- Pydantic / JSON Schema
- PyYAML
- PDF/form processing utilities
- Modular pipeline design

---

## Sample Synthetic Record

```json
{
  "taxpayer_id": "SYN-100245",
  "filing_status": "single",
  "wages": 72000,
  "interest_income": 340,
  "standard_deduction": 14600,
  "taxable_income": 57740,
  "federal_tax_withheld": 8200,
  "record_type": "synthetic"
}
```

---

## How It Works

```text
1. Generate a synthetic taxpayer identity
2. Simulate income and tax-related fields
3. Apply deduction, credit, and withholding logic
4. Map values into form-ready fields
5. Validate field consistency and schema rules
6. Export structured data or sample outputs
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sanskarhere/tax_synth.git
cd tax_synth
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate
```

```bash
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the pipeline

```bash
python main.py
```

---

## Current Scope

This project focuses on synthetic tax data generation, structured field preparation, validation logic, and form-ready output design.

It is intended for engineering experiments, portfolio demonstration, testing workflows, and document AI prototyping.

---

## Safety and Privacy

This repository is designed for **synthetic data only**.

Do not commit real taxpayer information, private identifiers, API keys, logs, or bulk generated outputs.

Recommended public-repo practice:

```text
Push:    source code, configs, schemas, small samples, redacted outputs
Ignore:  .env, real data, full generated datasets, logs, caches, bulk PDFs
```

---

## Disclaimer

This project generates fully synthetic tax data for software testing, research, and educational use.

It does not use, store, or process real taxpayer information. All names, identifiers, addresses, income values, and tax records are artificially generated.

This project is not tax advice and must not be used for filing real tax returns.

---

## Why It Stands Out

Most beginner AI projects stop at model training.

`tax_synth` focuses on a practical data engineering and document automation problem:

> How can teams safely test tax automation systems when real taxpayer data cannot be used?

This project demonstrates:

- synthetic data engineering
- privacy-aware data design
- document automation thinking
- rule-based validation
- cross-field consistency design
- modular Python engineering

---

## Roadmap

- Add support for more federal and state tax forms
- Generate filled PDF samples from mapped fields
- Add FastAPI endpoints for dataset generation
- Add database storage support
- Improve validation with configurable rule files
- Add synthetic dataset quality reports
- Add automated tests for edge cases

---

## Author

Built by Sanskar Gupta
AI/ML Engineer | Synthetic Data | Document Automation | Python

---

## License

This project is licensed under the MIT License.See the (LICENSE) file for details.
