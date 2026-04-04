from __future__ import annotations

from collections import defaultdict
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from tax_synth.models.case import TaxCase
from tax_synth.models.enums import FilingStatus

Rect = Tuple[float, float, float, float]


class IRSPacketRenderer:
    """Template-aware overlay renderer for the current IRS 1040 PDF.

    Uses the template's real widget rectangles for alignment, but writes visible
    text with ReportLab overlays instead of relying on fragile AcroForm appearance
    generation.
    """

    def __init__(self, templates_root: Path | None = None) -> None:
        if templates_root is None:
            templates_root = Path("templates/pdf/federal")
        self.templates_root = Path(templates_root)
        self.template_path = self._resolve_1040_template()
        self._page_rects = self._extract_widget_rects()

    def _resolve_1040_template(self) -> Path:
        candidates = [
            self.templates_root / "form_1040.pdf",
            Path("templates/pdf/federal/form_1040.pdf"),
            Path("templates/pdf/form_1040.pdf"),
        ]
        for c in candidates:
            if c.exists():
                return c
        raise FileNotFoundError("Could not find form_1040.pdf")

    def _extract_widget_rects(self) -> Dict[int, Dict[str, List[Rect]]]:
        reader = PdfReader(str(self.template_path))
        pages: Dict[int, Dict[str, List[Rect]]] = {}
        for page_idx, page in enumerate(reader.pages):
            field_map: Dict[str, List[Rect]] = defaultdict(list)
            annots_ref = page.get("/Annots")
            annots = annots_ref.get_object() if annots_ref else []
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
            for key, rects in field_map.items():
                field_map[key] = sorted(rects, key=lambda r: (-r[1], r[0]))
            pages[page_idx] = field_map
        return pages

    def _make_overlay(self, draw_callback) -> BytesIO:
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        draw_callback(c)
        c.save()
        packet.seek(0)
        return packet

    def _write_single_merged_page(
        self,
        overlay_stream: BytesIO,
        output_path: Path,
        template_page_index: int,
    ) -> None:
        template_reader = PdfReader(str(self.template_path))
        overlay_reader = PdfReader(overlay_stream)
        writer = PdfWriter()

        page = template_reader.pages[template_page_index]
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as f:
            writer.write(f)

    def _rect(self, page_index: int, field_name: str, idx: int = 0) -> Rect:
        rects = self._page_rects[page_index][field_name]
        return rects[idx]

    def _money(self, value: int | float | None) -> str:
        if value is None:
            return ""
        return str(int(round(value)))

    def _text(self, value: object | None) -> str:
        if value is None:
            return ""
        return str(value)

    def _signature_date(self, case: TaxCase) -> str:
        return f"04/15/{case.tax_year + 1}"

    def _draw_text_in_rect(
        self,
        c: canvas.Canvas,
        rect: Rect,
        text: str,
        *,
        font: str = "Helvetica",
        size: float = 9.0,
        align: str = "left",
        pad_left: float = 2.0,
        pad_right: float = 2.0,
    ) -> None:
        if text == "":
            return
        x0, y0, x1, y1 = rect
        c.setFont(font, size)
        baseline = y0 + max((y1 - y0 - size) / 2.0 + 0.5, 1.0)
        if align == "right":
            c.drawRightString(x1 - pad_right, baseline, text)
        elif align == "center":
            c.drawCentredString((x0 + x1) / 2.0, baseline, text)
        else:
            c.drawString(x0 + pad_left, baseline, text)

    def _draw_checkbox(self, c: canvas.Canvas, rect: Rect, *, size: float = 10.0) -> None:
        x0, y0, x1, y1 = rect
        c.setFont("Helvetica-Bold", size)
        c.drawCentredString((x0 + x1) / 2.0, y0 - 0.2, "X")

    def render_form_1040_page1(self, case: TaxCase, output_path: Path) -> None:
        page_index = 0

        def draw(c: canvas.Canvas) -> None:
            federal = case.federal_return
            if federal is None:
                raise ValueError("federal_return must exist before rendering page 1")

            self._draw_text_in_rect(c, self._rect(page_index, "f1_04[0]"), self._text(case.taxpayer.first_name), size=8.8)
            self._draw_text_in_rect(c, self._rect(page_index, "f1_05[0]"), self._text(case.taxpayer.last_name), size=8.8)
            self._draw_text_in_rect(c, self._rect(page_index, "f1_06[0]"), self._text(case.taxpayer.ssn), size=8.6)

            if case.spouse:
                self._draw_text_in_rect(c, self._rect(page_index, "f1_07[0]"), self._text(case.spouse.first_name), size=8.8)
                self._draw_text_in_rect(c, self._rect(page_index, "f1_08[0]"), self._text(case.spouse.last_name), size=8.8)
                self._draw_text_in_rect(c, self._rect(page_index, "f1_09[0]"), self._text(case.spouse.ssn), size=8.6)

            self._draw_text_in_rect(c, self._rect(page_index, "f1_10[0]"), self._text(case.address.street), size=8.8)
            self._draw_text_in_rect(c, self._rect(page_index, "f1_12[0]"), self._text(case.address.city), size=8.8)
            self._draw_text_in_rect(c, self._rect(page_index, "f1_13[0]"), self._text(case.address.state), size=8.8)
            self._draw_text_in_rect(c, self._rect(page_index, "f1_14[0]"), self._text(case.address.zip_code), size=8.8, align="right", pad_right=4)

            filing_rects = {
                FilingStatus.SINGLE: (102.799, 584.001, 110.799, 592.001),
                FilingStatus.MFJ: (102.799, 572.002, 110.799, 580.002),
                FilingStatus.MFS: (102.799, 560.0, 110.799, 568.0),
                FilingStatus.HOH: (369.199, 584.001, 377.199, 592.001),
                FilingStatus.QSS: (369.199, 560.0, 377.199, 568.0),
            }
            self._draw_checkbox(c, filing_rects[case.filing.federal_status], size=9.5)

            no_rect = sorted(self._page_rects[page_index]["c1_5[1]"], key=lambda r: (r[0], r[1]))[0]
            self._draw_checkbox(c, no_rect, size=9.5)

            dep_rows = [
                ("f1_20[0]", "f1_21[0]", "f1_22[0]", "c1_14[0]", "c1_15[0]"),
                ("f1_23[0]", "f1_24[0]", "f1_25[0]", "c1_16[0]", "c1_17[0]"),
                ("f1_26[0]", "f1_27[0]", "f1_28[0]", "c1_18[0]", "c1_19[0]"),
                ("f1_29[0]", "f1_30[0]", "f1_31[0]", "c1_20[0]", "c1_21[0]"),
            ]
            for dep, row in zip(case.dependents[:4], dep_rows):
                name_field, ssn_field, rel_field, ctc_box, other_box = row
                self._draw_text_in_rect(c, self._rect(page_index, name_field), dep.full_name, size=8.0)
                self._draw_text_in_rect(c, self._rect(page_index, ssn_field), dep.ssn, size=8.0, align="center")
                self._draw_text_in_rect(c, self._rect(page_index, rel_field), dep.relationship.value, size=8.0, align="center")
                self._draw_checkbox(c, self._rect(page_index, ctc_box if dep.qualifies_child_tax_credit else other_box), size=8.8)

            if len(case.dependents) > 4:
                self._draw_checkbox(c, self._rect(page_index, "c1_13[0]"), size=8.8)

            w2_wages = case.income_documents.w2.wages_box1 if case.income_documents.w2 else 0
            taxable_interest = case.income_documents.interest_1099_int.taxable_interest if case.income_documents.interest_1099_int else 0
            qualified_dividends = case.income_documents.dividend_1099_div.qualified_dividends if case.income_documents.dividend_1099_div else 0
            ordinary_dividends = case.income_documents.dividend_1099_div.ordinary_dividends if case.income_documents.dividend_1099_div else 0
            schedule_c_income = case.income_documents.schedule_c.net_profit if case.income_documents.schedule_c else 0

            amounts = {
                "f1_32[0]": w2_wages,
                "f1_41[0]": w2_wages,
                "f1_43[0]": taxable_interest,
                "f1_44[0]": qualified_dividends,
                "f1_45[0]": ordinary_dividends,
                "f1_53[0]": schedule_c_income,
                "f1_54[0]": federal.total_income,
                "f1_55[0]": federal.adjustments,
                "f1_56[0]": federal.agi,
                "f1_57[0]": federal.standard_deduction,
                "f1_58[0]": federal.qbi_deduction,
                "f1_59[0]": federal.standard_deduction + federal.qbi_deduction,
                "f1_60[0]": federal.taxable_income,
            }

            zeros = [
                "f1_33[0]", "f1_34[0]", "f1_35[0]", "f1_36[0]", "f1_37[0]",
                "f1_38[0]", "f1_39[0]", "f1_42[0]", "f1_46[0]", "f1_47[0]",
                "f1_48[0]", "f1_49[0]", "f1_50[0]", "f1_51[0]", "f1_52[0]",
            ]
            for field in zeros:
                if field in ["f1_42[0]", "f1_46[0]", "f1_48[0]", "f1_50[0]"]:
                    continue
                amounts[field] = 0

            for field, value in amounts.items():
                self._draw_text_in_rect(
                    c,
                    self._rect(page_index, field),
                    self._money(value),
                    size=8.8,
                    align="right",
                    pad_right=3,
                )

        overlay = self._make_overlay(draw)
        self._write_single_merged_page(overlay, output_path, page_index)

    def render_form_1040_page2(self, case: TaxCase, output_path: Path) -> None:
        page_index = 1

        def draw(c: canvas.Canvas) -> None:
            federal = case.federal_return
            if federal is None:
                raise ValueError("federal_return must exist before rendering page 2")
            federal_withholding = case.income_documents.w2.federal_withholding if case.income_documents.w2 else 0

            values = {
                "f2_02[0]": federal.tax_before_credits,
                "f2_03[0]": 0,
                "f2_04[0]": federal.tax_before_credits,
                "f2_05[0]": federal.child_tax_credit,
                "f2_06[0]": 0,
                "f2_07[0]": federal.child_tax_credit,
                "f2_08[0]": max(federal.tax_before_credits - federal.child_tax_credit, 0),
                "f2_09[0]": federal.self_employment_tax,
                "f2_10[0]": federal.total_tax,
                "f2_11[0]": federal_withholding,
                "f2_12[0]": 0,
                "f2_13[0]": 0,
                "f2_14[0]": federal_withholding,
                "f2_15[0]": 0,
                "f2_16[0]": 0,
                "f2_17[0]": 0,
                "f2_18[0]": 0,
                "f2_19[0]": 0,
                "f2_20[0]": 0,
                "f2_21[0]": 0,
                "f2_22[0]": federal.total_payments,
                "f2_23[0]": federal.refund,
                "f2_24[0]": federal.refund,
                "f2_27[0]": 0,
                "f2_28[0]": federal.balance_due,
                "f2_29[0]": 0,
            }

            for field, value in values.items():
                self._draw_text_in_rect(
                    c,
                    self._rect(page_index, field),
                    self._money(value),
                    size=8.8,
                    align="right",
                    pad_right=3,
                )

            c.setFont("Helvetica", 8.6)
            c.drawString(100, 301, case.taxpayer.full_name)
            c.drawCentredString(283, 301, self._signature_date(case))
            self._draw_text_in_rect(c, self._rect(page_index, "f2_33[0]"), self._text(case.taxpayer.occupation), size=8.6)

            if case.spouse:
                c.drawString(100, 271, case.spouse.full_name)
                c.drawCentredString(283, 271, self._signature_date(case))
                self._draw_text_in_rect(c, self._rect(page_index, "f2_35[0]"), self._text(case.spouse.occupation), size=8.6)

        overlay = self._make_overlay(draw)
        self._write_single_merged_page(overlay, output_path, page_index)