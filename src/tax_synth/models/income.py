from pydantic import BaseModel, Field, model_validator


class W2Income(BaseModel):
    employer_name: str
    wages_box1: int = Field(ge=0)
    federal_withholding: int = Field(ge=0)
    state_wages: int = Field(ge=0)
    state_withholding: int = Field(ge=0)


class InterestIncome(BaseModel):
    payer_name: str
    taxable_interest: int = Field(ge=0)


class DividendIncome(BaseModel):
    payer_name: str
    ordinary_dividends: int = Field(ge=0)
    qualified_dividends: int = Field(ge=0)

    @model_validator(mode="after")
    def qualified_not_more_than_ordinary(self) -> "DividendIncome":
        if self.qualified_dividends > self.ordinary_dividends:
            raise ValueError("qualified_dividends cannot exceed ordinary_dividends")
        return self


class ScheduleCIncome(BaseModel):
    business_name: str
    business_code: str
    business_description: str
    gross_receipts: int = Field(ge=0)
    total_expenses: int = Field(ge=0)
    depreciation: int = Field(ge=0, default=0)
    other_expenses: int = Field(ge=0, default=0)

    @property
    def net_profit(self) -> int:
        return self.gross_receipts - self.total_expenses