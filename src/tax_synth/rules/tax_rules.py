# src/tax_synth/rules/tax_rules.py

STANDARD_DEDUCTION = {
    2020: {"single": 12400, "mfj": 24800, "hoh": 18650},
    2021: {"single": 12550, "mfj": 25100, "hoh": 18800},
    2022: {"single": 12950, "mfj": 25900, "hoh": 19400},
    2023: {"single": 13850, "mfj": 27700, "hoh": 20800},
    2024: {"single": 14600, "mfj": 29200, "hoh": 21900},
    2025: {"single": 15750, "mfj": 31500, "hoh": 23625},
}

VALID_STATES = ["CA", "NY", "TX", "FL", "IL"]

VALID_TAX_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]


def normalize_filing_status(filing_status: str, dependents: list) -> str:
    """
    HOH requires at least one dependent.
    If no dependents, downgrade HOH -> Single.
    """
    filing_status = filing_status.lower().strip()

    if filing_status == "head_of_household":
        filing_status = "hoh"
    elif filing_status == "married_filing_jointly":
        filing_status = "mfj"

    if filing_status == "hoh" and len(dependents) == 0:
        return "single"

    return filing_status


def get_standard_deduction(tax_year: int, filing_status: str) -> int:
    filing_status = filing_status.lower().strip()

    if filing_status == "head_of_household":
        filing_status = "hoh"
    elif filing_status == "married_filing_jointly":
        filing_status = "mfj"

    if tax_year not in STANDARD_DEDUCTION:
        raise ValueError(f"Unsupported tax year: {tax_year}")

    if filing_status not in STANDARD_DEDUCTION[tax_year]:
        raise ValueError(f"Unsupported filing status: {filing_status}")

    return STANDARD_DEDUCTION[tax_year][filing_status]