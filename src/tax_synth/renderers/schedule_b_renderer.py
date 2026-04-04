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


class ScheduleBRenderer:
    def __init__(self, templates_root: Path | None = None) -> None:
        if templates_root is None:
            templates_root = Path("templates/pdf/federal")
        self.templates_root = Path(templates_root)
        self.template_path = self.templates_root / "schedule_b.pdf"
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
        size: float = 8.5,
        align: str = "left",
        pad_left: float = 2.0,
        pad_right: float = 3.0,
    ) -> None:
        if text == "":
            return
        x0, y0, x1, y1 = rect
        c.setFont("Helvetica", size)
        baseline = y0 + max((y1 - y0 - size) / 2.0 + 0.5, 1.0)
        if align == "right":
            c.drawRightString(x1 - pad_right, baseline, text)
        elif align == "center":
            c.drawCentredString((x0 + x1) / 2.0, baseline, text)
        else:
            c.drawString(x0 + pad_left, baseline, text)

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
        interest = case.income_documents.interest_1099_int
        dividend = case.income_documents.dividend_1099_div
        if not interest and not dividend:
            return None

        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)

        self._draw_text_in_rect(c, self._rect("f1_01[0]"), case.taxpayer.full_name)
        self._draw_text_in_rect(c, self._rect("f1_02[0]"), case.taxpayer.ssn)

        if interest:
            self._draw_text_in_rect(c, self._rect("f1_03[0]"), interest.payer_name)
            self._draw_text_in_rect(c, self._rect("f1_04[0]"), self._money(interest.taxable_interest), align="right")
            self._draw_text_in_rect(c, self._rect("f1_31[0]"), self._money(interest.taxable_interest), align="right")
            self._draw_text_in_rect(c, self._rect("f1_32[0]"), "0", align="right")
            self._draw_text_in_rect(c, self._rect("f1_33[0]"), self._money(interest.taxable_interest), align="right")
        else:
            for field in ["f1_31[0]", "f1_32[0]", "f1_33[0]"]:
                self._draw_text_in_rect(c, self._rect(field), "0", align="right")

        if dividend:
            self._draw_text_in_rect(c, self._rect("f1_34[0]"), dividend.payer_name)
            self._draw_text_in_rect(c, self._rect("f1_35[0]"), self._money(dividend.ordinary_dividends), align="right")
            self._draw_text_in_rect(c, self._rect("f1_64[0]"), self._money(dividend.ordinary_dividends), align="right")
        else:
            self._draw_text_in_rect(c, self._rect("f1_64[0]"), "0", align="right")

        c.save()
        packet.seek(0)
        self._merge_overlay(packet, output_path)
        return output_path
