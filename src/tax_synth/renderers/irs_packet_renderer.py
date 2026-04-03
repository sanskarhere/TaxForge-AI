from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from tax_synth.models.case import TaxCase


class IRSPacketRenderer:
    def _draw_label_value(
        self,
        c: canvas.Canvas,
        *,
        label: str,
        value: str,
        x_label: int,
        x_value: int,
        y: int,
        label_size: int = 9,
        value_size: int = 10,
    ) -> None:
        c.setFont("Helvetica", label_size)
        c.drawString(x_label, y, label)
        c.setFont("Helvetica-Bold", value_size)
        c.drawString(x_value, y, value)

    def _safe(self, value: object | None) -> str:
        if value is None:
            return ""
        return str(value)

    def render_form_1040_page1(self, case: TaxCase, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 40, "Form 1040 - U.S. Individual Income Tax Return (Synthetic)")
        c.setFont("Helvetica", 9)
        c.drawString(40, height - 55, f"Tax Year: {case.tax_year}")

        y = height - 90

        # Personal info
        self._draw_label_value(
            c,
            label="Taxpayer:",
            value=f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            x_label=40,
            x_value=130,
            y=y,
        )
        y -= 18

        self._draw_label_value(
            c,
            label="SSN:",
            value=self._safe(case.taxpayer.ssn),
            x_label=40,
            x_value=130,
            y=y,
        )
        y -= 18

        spouse_name = ""
        spouse_ssn = ""
        if case.spouse:
            spouse_name = f"{case.spouse.first_name} {case.spouse.last_name}"
            spouse_ssn = self._safe(case.spouse.ssn)

        self._draw_label_value(
            c,
            label="Spouse:",
            value=spouse_name,
            x_label=40,
            x_value=130,
            y=y,
        )
        y -= 18

        self._draw_label_value(
            c,
            label="Spouse SSN:",
            value=spouse_ssn,
            x_label=40,
            x_value=130,
            y=y,
        )
        y -= 18

        self._draw_label_value(
            c,
            label="Address:",
            value=f"{case.address.street}, {case.address.city}, {case.address.state} {case.address.zip_code}",
            x_label=40,
            x_value=130,
            y=y,
        )
        y -= 18

        self._draw_label_value(
            c,
            label="Filing Status:",
            value=self._safe(case.filing.federal_status),
            x_label=40,
            x_value=130,
            y=y,
        )
        y -= 28

        # Dependents
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Dependents")
        y -= 18

        c.setFont("Helvetica", 10)
        if case.dependents:
            for dep in case.dependents[:4]:
                dep_line = f"{dep.first_name} {dep.last_name} | {dep.relationship} | {dep.ssn}"
                c.drawString(50, y, dep_line)
                y -= 16
        else:
            c.drawString(50, y, "None")
            y -= 16

        y -= 10

        # Income section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Income")
        y -= 20

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
            case.income_documents.schedule_c.net_profit if case.income_documents.schedule_c else 0
        )

        self._draw_label_value(c, label="W-2 Wages:", value=f"${w2:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="Taxable Interest:", value=f"${interest:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="Ordinary Dividends:", value=f"${dividends:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="Schedule C Profit:", value=f"${schedule_c_profit:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="Total Income:", value=f"${case.federal_return.total_income:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="Adjustments:", value=f"${case.federal_return.adjustments:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="AGI:", value=f"${case.federal_return.agi:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="Standard Deduction:", value=f"${case.federal_return.standard_deduction:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="QBI Deduction:", value=f"${case.federal_return.qbi_deduction:,}", x_label=40, x_value=200, y=y)
        y -= 18
        self._draw_label_value(c, label="Taxable Income:", value=f"${case.federal_return.taxable_income:,}", x_label=40, x_value=200, y=y)

        c.save()

    def render_form_1040_page2(self, case: TaxCase, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 40, "Form 1040 - Tax and Payments (Synthetic)")
        c.setFont("Helvetica", 9)
        c.drawString(40, height - 55, f"Case ID: {case.case_id}")

        y = height - 90

        self._draw_label_value(
            c,
            label="Taxpayer:",
            value=f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            x_label=40,
            x_value=130,
            y=y,
        )
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Tax and Credits")
        y -= 20

        self._draw_label_value(c, label="Tax Before Credits:", value=f"${case.federal_return.tax_before_credits:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="Child Tax Credit:", value=f"${case.federal_return.child_tax_credit:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="Self-Employment Tax:", value=f"${case.federal_return.self_employment_tax:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="Total Tax:", value=f"${case.federal_return.total_tax:,}", x_label=40, x_value=220, y=y)

        y -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Payments")
        y -= 20

        w2_withholding = case.income_documents.w2.federal_withholding if case.income_documents.w2 else 0

        self._draw_label_value(c, label="Federal Withholding:", value=f"${w2_withholding:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="Total Payments:", value=f"${case.federal_return.total_payments:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="Refund:", value=f"${case.federal_return.refund:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="Balance Due:", value=f"${case.federal_return.balance_due:,}", x_label=40, x_value=220, y=y)

        y -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "State Return")
        y -= 20

        self._draw_label_value(c, label="State Code:", value=case.state_return.state_code, x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="State AGI:", value=f"${case.state_return.state_agi:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="State Taxable Income:", value=f"${case.state_return.taxable_income:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="State Total Tax:", value=f"${case.state_return.total_tax:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="State Refund:", value=f"${case.state_return.refund:,}", x_label=40, x_value=220, y=y)
        y -= 18
        self._draw_label_value(c, label="State Balance Due:", value=f"${case.state_return.balance_due:,}", x_label=40, x_value=220, y=y)

        c.save()