from reportlab.pdfgen import canvas
from pathlib import Path

from tax_synth.models.case import TaxCase


class StateRenderer:
    def render(self, case: TaxCase, output_path: Path):
        state = case.state_return

        c = canvas.Canvas(str(output_path))

        c.drawString(100, 750, f"{state.state_code} State Tax Return")

        c.drawString(100, 700, f"State AGI: {state.state_agi}")
        c.drawString(100, 680, f"Taxable Income: {state.taxable_income}")
        c.drawString(100, 660, f"Total Tax: {state.total_tax}")
        c.drawString(100, 640, f"Refund: {state.refund}")
        c.drawString(100, 620, f"Balance Due: {state.balance_due}")

        c.save()
        return output_path