from __future__ import annotations

from tax_synth.models.california import CaliforniaReturn
from tax_synth.models.case import TaxCase

CA_STANDARD_DEDUCTION_MFJ_2024 = 11_080
CA_DEPENDENT_EXEMPTION_CREDIT = 461
CA_PERSONAL_EXEMPTION_CREDIT = 149


def simple_ca_tax(taxable_income: int) -> int:
    if taxable_income <= 0:
        return 0
    if taxable_income <= 20_000:
        return round(taxable_income * 0.01)
    if taxable_income <= 50_000:
        return round(20_000 * 0.01 + (taxable_income - 20_000) * 0.02)
    return round(20_000 * 0.01 + 30_000 * 0.02 + (taxable_income - 50_000) * 0.04)


def build_california_return(case: TaxCase) -> CaliforniaReturn:
    if case.federal_return is None:
        raise ValueError("Federal return must be computed before California return")

    additions = 0
    subtractions = 0

    # In the sample, CA adds back some federal-specific deductions,
    # so this structure is ready for those adjustments.
    ca_agi = case.federal_return.agi + additions - subtractions
    taxable_income = max(0, ca_agi - CA_STANDARD_DEDUCTION_MFJ_2024)

    tax_before_credits = simple_ca_tax(taxable_income)

    exemption_credits = 2 * CA_PERSONAL_EXEMPTION_CREDIT
    exemption_credits += len(case.dependents) * CA_DEPENDENT_EXEMPTION_CREDIT

    total_tax = max(0, tax_before_credits - exemption_credits)

    total_payments = 0
    if case.income_documents.w2:
        total_payments += case.income_documents.w2.state_withholding

    refund = max(0, total_payments - total_tax)
    balance_due = max(0, total_tax - total_payments)

    return CaliforniaReturn(
        california_adjustments_additions=additions,
        california_adjustments_subtractions=subtractions,
        ca_agi=ca_agi,
        standard_deduction=CA_STANDARD_DEDUCTION_MFJ_2024,
        taxable_income=taxable_income,
        tax_before_credits=tax_before_credits,
        exemption_credits=exemption_credits,
        total_tax=total_tax,
        total_payments=total_payments,
        refund=refund,
        balance_due=balance_due,
    )