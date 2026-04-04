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


class ScheduleSERenderer:
    def __init__(self, templates_root: Path | None = None) -> None:
        if templates_root is None:
            templates_root = Path("templates/pdf/federal")
        self.templates_root = Path(templates_root)
        self.template_path = self.templates_root / "schedule_se.pdf"
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
        sc = case.income_documents.schedule_c
        if not sc:
            return None

        net_profit = sc.net_profit
        se_base = round(net_profit * 0.9235)
        line10_ss_tax = round(se_base * 0.124)
        line11_medicare_tax = round(se_base * 0.029)
        se_tax = line10_ss_tax + line11_medicare_tax
        half_se_deduction = round(se_tax * 0.50)

        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)

        self._draw_text_in_rect(c, self._rect("f1_1[0]"), case.taxpayer.full_name)
        self._draw_text_in_rect(c, self._rect("f1_2[0]"), case.taxpayer.ssn)

        # Part I lines
        values = {
            "f1_3[0]": 0,              # 1a
            # f1_4 is 1b parenthetical, leave blank
            "f1_5[0]": net_profit,     # 2
            "f1_6[0]": net_profit,     # 3
            "f1_7[0]": se_base,        # 4a
            "f1_8[0]": 0,              # 4b
            "f1_9[0]": se_base,        # 4c
            # f1_10 5a blank
            "f1_11[0]": 0,             # 5b
            "f1_12[0]": se_base,       # 6
            "f1_14[0]": 0,             # 8a wages
            "f1_15[0]": 0,             # 8b
            "f1_16[0]": 0,             # 8c
            "f1_17[0]": 0,             # 8d
            "f1_18[0]": 168600,        # 9
            "f1_19[0]": line10_ss_tax, # 10
            "f1_20[0]": line11_medicare_tax, #11
            "f1_21[0]": se_tax,        # 12
            "f1_22[0]": half_se_deduction,   # 13
        }
        for field, value in values.items():
            self._draw_text_in_rect(c, self._rect(field), self._money(value), align="right")

        # line 7 has a broken rect in the PDF; place manually in its visible box
        c.setFont("Helvetica", 8.5)
        c.drawRightString(545, 389, "168,600")

        c.save()
        packet.seek(0)
        self._merge_overlay(packet, output_path)
        return output_path
