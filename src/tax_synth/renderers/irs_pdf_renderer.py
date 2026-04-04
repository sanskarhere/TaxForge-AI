from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

from tax_synth.models.case import TaxCase


class IRSPacketRenderer:
    def render(self, case: TaxCase, output_path: Path):
        c = canvas.Canvas(str(output_path), pagesize=letter)

        y = 750

        def line(text):
            nonlocal y
            c.drawString(50, y, text)
            y -= 20

        # Header
        c.setFont("Helvetica-Bold", 14)
        line("U.S. Individual Income Tax Return (Synthetic)")

        c.setFont("Helvetica", 10)
        line(f"Name: {case.taxpayer.first_name} {case.taxpayer.last_name}")
        if case.spouse:
            line(f"Spouse: {case.spouse.first_name} {case.spouse.last_name}")

        line(f"SSN: {case.taxpayer.ssn}")
        line(f"Address: {case.address.street}, {case.address.city}, {case.address.state}")

        y -= 10
        line("----- INCOME -----")
        line(f"Wages: {case.income_documents.w2.wages_box1}")

        y -= 10
        line("----- TAX CALCULATION -----")
        fr = case.federal_return

        line(f"Total Income: {fr.total_income}")
        line(f"AGI: {fr.agi}")
        line(f"Standard Deduction: {fr.standard_deduction}")
        line(f"Taxable Income: {fr.taxable_income}")

        y -= 10
        line("----- TAX -----")
        line(f"Tax Before Credits: {fr.tax_before_credits}")
        line(f"Child Tax Credit: {fr.child_tax_credit}")
        line(f"Total Tax: {fr.total_tax}")

        y -= 10
        line("----- PAYMENTS -----")
        line(f"Total Payments: {fr.total_payments}")

        y -= 10
        line("----- RESULT -----")
        line(f"Refund: {fr.refund}")
        line(f"Balance Due: {fr.balance_due}")

        c.save()