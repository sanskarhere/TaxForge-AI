from __future__ import annotations

from tax_synth.models.california import StateReturn
from tax_synth.models.case import TaxCase

STATE_STANDARD_DEDUCTION = {
    "CA": 11_080,
    "TX": 0,
    "NY": 8_000,
    "FL": 0,
    "WA": 0,
}

STATE_PERSONAL_EXEMPTION_CREDIT = {
    "CA": 149,
    "TX": 0,
    "NY": 100,
    "FL": 0,
    "WA": 0,
}

STATE_DEPENDENT_EXEMPTION_CREDIT = {
    "CA": 461,
    "TX": 0,
    "NY": 100,
    "FL": 0,
    "WA": 0,
}


def simple_state_tax(state_code: str, taxable_income: int) -> int:
    if taxable_income <= 0:
        return 0

    if state_code in {"TX", "FL", "WA"}:
        return 0

    if state_code == "CA":
        if taxable_income <= 20_000:
            return round(taxable_income * 0.01)
        if taxable_income <= 50_000:
            return round(20_000 * 0.01 + (taxable_income - 20_000) * 0.02)
        return round(20_000 * 0.01 + 30_000 * 0.02 + (taxable_income - 50_000) * 0.04)

    if state_code == "NY":
        if taxable_income <= 20_000:
            return round(taxable_income * 0.02)
        if taxable_income <= 50_000:
            return round(20_000 * 0.02 + (taxable_income - 20_000) * 0.04)
        return round(20_000 * 0.02 + 30_000 * 0.04 + (taxable_income - 50_000) * 0.055)

    return 0


def build_california_return(case: TaxCase) -> StateReturn:
    if case.federal_return is None:
        raise ValueError("Federal return must be computed before state return")

    state_code = case.filing.residency_state

    additions = 0
    subtractions = 0

    state_agi = case.federal_return.agi + additions - subtractions
    standard_deduction = STATE_STANDARD_DEDUCTION.get(state_code, 0)
    taxable_income = max(0, state_agi - standard_deduction)

    tax_before_credits = simple_state_tax(state_code, taxable_income)

    personal_credit = STATE_PERSONAL_EXEMPTION_CREDIT.get(state_code, 0)
    dependent_credit = STATE_DEPENDENT_EXEMPTION_CREDIT.get(state_code, 0)

    exemption_credits = 0
    if case.filing.federal_status.value == "married_filing_jointly":
        exemption_credits += personal_credit * 2
    else:
        exemption_credits += personal_credit

    exemption_credits += len(case.dependents) * dependent_credit

    total_tax = max(0, tax_before_credits - exemption_credits)

    total_payments = 0
    if case.income_documents.w2:
        total_payments += case.income_documents.w2.state_withholding

    refund = max(0, total_payments - total_tax)
    balance_due = max(0, total_tax - total_payments)

    return StateReturn(
        state_code=state_code,
        state_adjustments_additions=additions,
        state_adjustments_subtractions=subtractions,
        state_agi=state_agi,
        standard_deduction=standard_deduction,
        taxable_income=taxable_income,
        tax_before_credits=tax_before_credits,
        exemption_credits=exemption_credits,
        total_tax=total_tax,
        total_payments=total_payments,
        refund=refund,
        balance_due=balance_due,
    )