from pydantic import BaseModel, Field


class StateReturn(BaseModel):
    state_code: str = Field(min_length=2, max_length=2)

    state_adjustments_additions: int = Field(ge=0, default=0)
    state_adjustments_subtractions: int = Field(ge=0, default=0)

    state_agi: int = Field(ge=0)
    standard_deduction: int = Field(ge=0)
    taxable_income: int = Field(ge=0)

    tax_before_credits: int = Field(ge=0)
    exemption_credits: int = Field(ge=0, default=0)
    total_tax: int = Field(ge=0)

    total_payments: int = Field(ge=0, default=0)
    refund: int = Field(ge=0, default=0)
    balance_due: int = Field(ge=0, default=0)