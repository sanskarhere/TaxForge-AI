from __future__ import annotations

from tax_synth.models.case import TaxCase
from tax_synth.models.enums import FilingStatus
from tax_synth.models.federal import FederalReturn

STANDARD_DEDUCTION = {
    2020: {
        FilingStatus.SINGLE: 12_400,
        FilingStatus.MFJ: 24_800,
        FilingStatus.HOH: 18_650,
    },
    2021: {
        FilingStatus.SINGLE: 12_550,
        FilingStatus.MFJ: 25_100,
        FilingStatus.HOH: 18_800,
    },
    2022: {
        FilingStatus.SINGLE: 12_950,
        FilingStatus.MFJ: 25_900,
        FilingStatus.HOH: 19_400,
    },
    2023: {
        FilingStatus.SINGLE: 13_850,
        FilingStatus.MFJ: 27_700,
        FilingStatus.HOH: 20_800,
    },
    2024: {
        FilingStatus.SINGLE: 14_600,
        FilingStatus.MFJ: 29_200,
        FilingStatus.HOH: 21_900,
    },
    2025: {
        FilingStatus.SINGLE: 15_000,
        FilingStatus.MFJ: 30_000,
        FilingStatus.HOH: 22_500,
    },
}


def compute_qbi_deduction(schedule_c_profit: int) -> int:
    if schedule_c_profit <= 0:
        return 0
    return round(schedule_c_profit * 0.20)


def compute_self_employment_tax(schedule_c_profit: int) -> tuple[int, int]:
    if schedule_c_profit <= 0:
        return 0, 0

    se_base = round(schedule_c_profit * 0.9235)
    se_tax = round((se_base * 0.124) + (se_base * 0.029))
    se_tax_deduction = round(se_tax * 0.50)
    return se_tax, se_tax_deduction


def simple_federal_tax(taxable_income: int, filing_status: FilingStatus) -> int:
    """
    Simplified synthetic tax calculator.
    Not intended for legal filing use.
    Good enough for internal consistency + realistic variation.
    """

    if taxable_income <= 0:
        return 0

    # Simple brackets by filing status
    if filing_status == FilingStatus.MFJ:
        if taxable_income <= 20_000:
            return round(taxable_income * 0.10)
        if taxable_income <= 80_000:
            return round(20_000 * 0.10 + (taxable_income - 20_000) * 0.12)
        return round(20_000 * 0.10 + 60_000 * 0.12 + (taxable_income - 80_000) * 0.22)

    if filing_status == FilingStatus.HOH:
        if taxable_income <= 15_000:
            return round(taxable_income * 0.10)
        if taxable_income <= 60_000:
            return round(15_000 * 0.10 + (taxable_income - 15_000) * 0.12)
        return round(15_000 * 0.10 + 45_000 * 0.12 + (taxable_income - 60_000) * 0.22)

    # SINGLE fallback
    if taxable_income <= 11_000:
        return round(taxable_income * 0.10)
    if taxable_income <= 45_000:
        return round(11_000 * 0.10 + (taxable_income - 11_000) * 0.12)
    return round(11_000 * 0.10 + 34_000 * 0.12 + (taxable_income - 45_000) * 0.22)


def build_federal_return(case: TaxCase) -> FederalReturn:
    # Safe extraction of income
    w2 = case.income_documents.w2.wages_box1 if case.income_documents.w2 else 0

    interest = (
        case.income_documents.interest_1099_int.taxable_interest
        if case.income_documents.interest_1099_int
        else 0
    )

    dividends = (
        case.income_documents.dividend_1099_div.ordinary_dividends
        if case.income_documents.dividend_1099_div
        else 0
    )

    schedule_c_profit = (
        case.income_documents.schedule_c.net_profit
        if case.income_documents.schedule_c
        else 0
    )

    total_income = w2 + interest + dividends + schedule_c_profit

    se_tax, se_tax_deduction = compute_self_employment_tax(schedule_c_profit)
    agi = max(0, total_income - se_tax_deduction)

    filing_status = case.filing.federal_status
    standard_deduction = STANDARD_DEDUCTION[case.tax_year][filing_status]

    qbi = compute_qbi_deduction(max(schedule_c_profit - se_tax_deduction, 0))
    taxable_income = max(0, agi - standard_deduction - qbi)

    tax_before_credits = simple_federal_tax(taxable_income, filing_status)

    child_tax_credit = 0
    for dep in case.dependents:
        child_tax_credit += 2000 if dep.qualifies_child_tax_credit else 500

    total_tax = max(0, tax_before_credits - child_tax_credit) + se_tax

    total_payments = 0
    if case.income_documents.w2:
        total_payments += case.income_documents.w2.federal_withholding

    refund = max(0, total_payments - total_tax)
    balance_due = max(0, total_tax - total_payments)

    return FederalReturn(
        total_income=total_income,
        adjustments=se_tax_deduction,
        agi=agi,
        standard_deduction=standard_deduction,
        qbi_deduction=qbi,
        taxable_income=taxable_income,
        tax_before_credits=tax_before_credits,
        child_tax_credit=child_tax_credit,
        self_employment_tax=se_tax,
        total_tax=total_tax,
        total_payments=total_payments,
        refund=refund,
        balance_due=balance_due,
    )