from pydantic import BaseModel, Field


class FederalReturn(BaseModel):
    total_income: int = Field(ge=0)
    adjustments: int = Field(ge=0)
    agi: int = Field(ge=0)

    standard_deduction: int = Field(ge=0)
    qbi_deduction: int = Field(ge=0, default=0)
    taxable_income: int = Field(ge=0)

    tax_before_credits: int = Field(ge=0)
    child_tax_credit: int = Field(ge=0, default=0)
    self_employment_tax: int = Field(ge=0, default=0)
    total_tax: int = Field(ge=0)

    total_payments: int = Field(ge=0, default=0)
    refund: int = Field(ge=0, default=0)
    balance_due: int = Field(ge=0, default=0)