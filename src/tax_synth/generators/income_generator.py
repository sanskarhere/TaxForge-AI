from __future__ import annotations

import random

from tax_synth.models.income import DividendIncome, InterestIncome, ScheduleCIncome, W2Income


class IncomeGenerator:
    def __init__(self, seed: int = 42) -> None:
        random.seed(seed)

    def build_w2(self, employer_name: str) -> W2Income | None:
        # 80% cases me W2 ho
        if random.random() < 0.2:
            return None

        wages = random.randint(42000, 90000)
        fed_withholding = round(wages * random.uniform(0.08, 0.16))
        ca_withholding = round(wages * random.uniform(0.02, 0.05))

        return W2Income(
            employer_name=employer_name,
            wages_box1=wages,
            federal_withholding=fed_withholding,
            state_wages=wages,
            state_withholding=ca_withholding,
        )

    def build_interest(self) -> InterestIncome | None:
        # 70% cases me interest ho
        if random.random() < 0.3:
            return None

        return InterestIncome(
            payer_name="Golden State Community Bank",
            taxable_interest=random.randint(50, 1500),
        )

    def build_dividends(self) -> DividendIncome | None:
        # 60% cases me dividend ho
        if random.random() < 0.4:
            return None

        ordinary = random.randint(100, 4000)
        qualified = random.randint(0, ordinary)
        return DividendIncome(
            payer_name="Charles Schwab Investments",
            ordinary_dividends=ordinary,
            qualified_dividends=qualified,
        )

    def build_schedule_c(self) -> ScheduleCIncome | None:
        # 50% cases me business income ho
        if random.random() < 0.5:
            return None

        gross = random.randint(30000, 120000)
        expense_ratio = random.uniform(0.25, 0.55)
        expenses = round(gross * expense_ratio)

        return ScheduleCIncome(
            business_name="Creative Studio LLC",
            business_code="541510",
            business_description="Freelance Graphic & Web Design",
            gross_receipts=gross,
            total_expenses=expenses,
            depreciation=random.randint(0, 2500),
            other_expenses=random.randint(0, 3000),
        )