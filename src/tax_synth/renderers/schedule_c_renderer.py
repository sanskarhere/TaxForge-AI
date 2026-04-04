from __future__ import annotations

from collections import defaultdict
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from tax_synth.models.case import TaxCase

Rect = Tuple[float, float, float, float]


class ScheduleCRenderer:
    def __init__(self, templates_root: Path | None = None) -> None:
        if templates_root is None:
            templates_root = Path("templates/pdf/federal")
        self.templates_root = Path(templates_root)
        self.template_path = self.templates_root / "schedule_c.pdf"
        self._rects = self._extract_widget_rects()

    def _extract_widget_rects(self) -> Dict[str, List[Rect]]:
        reader = PdfReader(str(self.template_path))
        page = reader.pages[0]
        annots = page.get("/Annots") or []
        field_map: Dict[str, List[Rect]] = defaultdict(list)
        for annot_ref in annots:
            annot = annot_ref.get_object()
            parent = annot.get("/Parent")
            if parent:
                parent = parent.get_object()
            name = annot.get("/T") or (parent.get("/T") if parent else None)
            rect = annot.get("/Rect")
            if not name or not rect:
                continue
            x0, y0, x1, y1 = [float(v) for v in rect]
            field_map[str(name)].append((x0, y0, x1, y1))
        return field_map

    def _rect(self, field_name: str, idx: int = 0) -> Rect:
        return self._rects[field_name][idx]

    def _money(self, value: int | float | None) -> str:
        if value is None:
            return ""
        return str(int(round(value)))

    def _draw_text_in_rect(
        self,
        c: canvas.Canvas,
        rect: Rect,
        text: str,
        *,
        size: float = 8.4,
        align: str = "left",
        pad_left: float = 2.0,
        pad_right: float = 3.0,
    ) -> None:
        if text == "":
            return
        x0, y0, x1, y1 = rect
        c.setFont("Helvetica", size)
        baseline = y0 + max((y1 - y0 - size) / 2.0 + 0.4, 1.0)
        if align == "right":
            c.drawRightString(x1 - pad_right, baseline, text)
        elif align == "center":
            c.drawCentredString((x0 + x1) / 2.0, baseline, text)
        else:
            c.drawString(x0 + pad_left, baseline, text)

    def _draw_checkbox(self, c: canvas.Canvas, rect: Rect, *, size: float = 9.0) -> None:
        x0, y0, x1, y1 = rect
        c.setFont("Helvetica-Bold", size)
        c.drawCentredString((x0 + x1) / 2.0, y0 - 0.3, "X")

    def _merge_overlay(self, overlay_stream: BytesIO, output_path: Path) -> None:
        base_reader = PdfReader(str(self.template_path))
        overlay_reader = PdfReader(overlay_stream)
        writer = PdfWriter()
        page = base_reader.pages[0]
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as f:
            writer.write(f)

    def render(self, case: TaxCase, output_path: Path):
        sc = case.income_documents.schedule_c
        if not sc:
            return None

        gross = sc.gross_receipts
        returns_allowances = 0
        gross_after_returns = gross
        cost_of_goods_sold = 0
        gross_profit = gross
        other_income = 0
        gross_income = gross

        depreciation = sc.depreciation
        other_expenses = sc.other_expenses
        office_expense = max(sc.total_expenses - depreciation - other_expenses, 0)
        total_expenses = office_expense + depreciation + other_expenses
        tentative_profit = gross_income - total_expenses
        home_use = 0
        net_profit = sc.net_profit

        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)

        # Header fields
        self._draw_text_in_rect(c, self._rect("f1_1[0]"), case.taxpayer.full_name)
        self._draw_text_in_rect(c, self._rect("f1_2[0]"), case.taxpayer.ssn)
        self._draw_text_in_rect(c, self._rect("f1_3[0]"), sc.business_description)
        self._draw_text_in_rect(c, self._rect("f1_4[0]"), sc.business_code, align="center")
        self._draw_text_in_rect(c, self._rect("f1_5[0]"), sc.business_name)
        self._draw_text_in_rect(c, self._rect("f1_7[0]"), case.address.street)
        self._draw_text_in_rect(c, self._rect("f1_8[0]"), f"{case.address.city}, {case.address.state} {case.address.zip_code}")

        # Checkboxes: cash accounting, materially participate yes, didn't start this year, no 1099, no 1099 filing
        self._draw_checkbox(c, self._rect("c1_1[0]"))
        self._draw_checkbox(c, self._rect("c1_2[0]"))
        self._draw_checkbox(c, self._rect("c1_4[1]"))
        self._draw_checkbox(c, self._rect("c1_5[1]"))

        # Part I income
        income_values = {
            "f1_10[0]": gross,
            "f1_11[0]": returns_allowances,
            "f1_12[0]": gross_after_returns,
            "f1_13[0]": cost_of_goods_sold,
            "f1_14[0]": gross_profit,
            "f1_15[0]": other_income,
            "f1_16[0]": gross_income,
        }
        for field, value in income_values.items():
            self._draw_text_in_rect(c, self._rect(field), self._money(value), align="right")

        # Part II expenses - only populate meaningful fields
        expense_values = {
            "f1_22[0]": depreciation,     # line 13
            "f1_28[0]": office_expense,   # line 18
            "f1_39[0]": other_expenses,   # line 27a
            "f1_40[0]": 0,                # line 27b
            "f1_41[0]": total_expenses,   # line 28
            "f1_42[0]": tentative_profit, # line 29
            "f1_45[0]": home_use,         # line 30
            "f1_46[0]": net_profit,       # line 31
        }
        for field, value in expense_values.items():
            self._draw_text_in_rect(c, self._rect(field), self._money(value), align="right")

        c.save()
        packet.seek(0)
        self._merge_overlay(packet, output_path)
        return output_path
