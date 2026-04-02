from pydantic import BaseModel, Field


class CaliforniaReturn(BaseModel):
    california_adjustments_additions: int = Field(ge=0, default=0)
    california_adjustments_subtractions: int = Field(ge=0, default=0)

    ca_agi: int = Field(ge=0)
    standard_deduction: int = Field(ge=0)
    taxable_income: int = Field(ge=0)

    tax_before_credits: int = Field(ge=0)
    exemption_credits: int = Field(ge=0, default=0)
    total_tax: int = Field(ge=0)

    total_payments: int = Field(ge=0, default=0)
    refund: int = Field(ge=0, default=0)
    balance_due: int = Field(ge=0, default=0)