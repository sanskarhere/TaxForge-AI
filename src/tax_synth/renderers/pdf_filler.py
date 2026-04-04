from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from tax_synth.models.case import TaxCase
from tax_synth.models.enums import FilingStatus
from tax_synth.renderers.pdf_form_filler import PDFFormFiller


class PDF1040Filler:
    """Hybrid 1040 renderer.

    Uses real AcroForm fields everywhere the IRS template exposes a field.
    Uses a tiny overlay only for taxpayer/spouse signature names + dates,
    because those visible signature lines are not backed by fillable widgets
    in this IRS template.
    """

    def __init__(self, template_path: Path) -> None:
        self.template_path = Path(template_path)
        self.form_filler = PDFFormFiller()

    def _text(self, value: object | None) -> str:
        return "" if value is None else str(value)

    def _money(self, value: int | float | None) -> str:
        if value is None:
            return ""
        return str(int(round(value)))

    def _signature_date(self, tax_year: int) -> str:
        return f"04/15/{tax_year + 1}"

    def _status_checkbox(self, case: TaxCase) -> dict[str, str]:
        status = case.filing.federal_status
        mapping = {
            FilingStatus.SINGLE: {
                "topmostSubform[0].Page1[0].FilingStatus_ReadOrder[0].c1_3[0]": "/1",
            },
            FilingStatus.MFJ: {
                "topmostSubform[0].Page1[0].FilingStatus_ReadOrder[0].c1_3[1]": "/3",
            },
            FilingStatus.MFS: {
                "topmostSubform[0].Page1[0].FilingStatus_ReadOrder[0].c1_3[2]": "/4",
            },
            FilingStatus.HOH: {
                "topmostSubform[0].Page1[0].c1_3[0]": "/2",
            },
            FilingStatus.QSS: {
                "topmostSubform[0].Page1[0].c1_3[1]": "/5",
            },
        }
        return mapping[status]

    def _dependent_fields(self, case: TaxCase) -> dict[str, str]:
        values: dict[str, str] = {}
        row_map = [
            {
                "name": "topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].f1_20[0]",
                "ssn": "topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].f1_21[0]",
                "rel": "topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].f1_22[0]",
                "ctc": "topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].c1_14[0]",
                "other": "topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].c1_15[0]",
            },
            {
                "name": "topmostSubform[0].Page1[0].Table_Dependents[0].Row2[0].f1_23[0]",
                "ssn": "topmostSubform[0].Page1[0].Table_Dependents[0].Row2[0].f1_24[0]",
                "rel": "topmostSubform[0].Page1[0].Table_Dependents[0].Row2[0].f1_25[0]",
                "ctc": "topmostSubform[0].Page1[0].Table_Dependents[0].Row2[0].c1_16[0]",
                "other": "topmostSubform[0].Page1[0].Table_Dependents[0].Row2[0].c1_17[0]",
            },
            {
                "name": "topmostSubform[0].Page1[0].Table_Dependents[0].Row3[0].f1_26[0]",
                "ssn": "topmostSubform[0].Page1[0].Table_Dependents[0].Row3[0].f1_27[0]",
                "rel": "topmostSubform[0].Page1[0].Table_Dependents[0].Row3[0].f1_28[0]",
                "ctc": "topmostSubform[0].Page1[0].Table_Dependents[0].Row3[0].c1_18[0]",
                "other": "topmostSubform[0].Page1[0].Table_Dependents[0].Row3[0].c1_19[0]",
            },
            {
                "name": "topmostSubform[0].Page1[0].Table_Dependents[0].Row4[0].f1_29[0]",
                "ssn": "topmostSubform[0].Page1[0].Table_Dependents[0].Row4[0].f1_30[0]",
                "rel": "topmostSubform[0].Page1[0].Table_Dependents[0].Row4[0].f1_31[0]",
                "ctc": "topmostSubform[0].Page1[0].Table_Dependents[0].Row4[0].c1_20[0]",
                "other": "topmostSubform[0].Page1[0].Table_Dependents[0].Row4[0].c1_21[0]",
            },
        ]

        for dep, row in zip(case.dependents[:4], row_map):
            values[row["name"]] = dep.full_name
            values[row["ssn"]] = dep.ssn
            values[row["rel"]] = dep.relationship.value
            values[row["ctc"] if dep.qualifies_child_tax_credit else row["other"]] = "/1"

        if len(case.dependents) > 4:
            values["topmostSubform[0].Page1[0].Dependents_ReadOrder[0].c1_13[0]"] = "/1"

        return values

    def build_field_values(self, case: TaxCase) -> dict[str, str]:
        w2 = case.income_documents.w2
        interest = case.income_documents.interest_1099_int
        dividends = case.income_documents.dividend_1099_div
        schedule_c = case.income_documents.schedule_c
        federal = case.federal_return

        if federal is None:
            raise ValueError("federal_return must be present before filling Form 1040")

        values: dict[str, str] = {
            "topmostSubform[0].Page1[0].f1_01[0]": self._text(case.taxpayer.first_name),
            "topmostSubform[0].Page1[0].f1_02[0]": self._text(case.taxpayer.last_name),
            "topmostSubform[0].Page1[0].f1_03[0]": self._text(case.taxpayer.ssn),
            "topmostSubform[0].Page1[0].f1_04[0]": self._text(case.spouse.first_name if case.spouse else ""),
            "topmostSubform[0].Page1[0].f1_05[0]": self._text(case.spouse.last_name if case.spouse else ""),
            "topmostSubform[0].Page1[0].f1_06[0]": self._text(case.spouse.ssn if case.spouse else ""),

            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_10[0]": self._text(case.address.street),
            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_11[0]": "",
            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_12[0]": self._text(case.address.city),
            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_13[0]": self._text(case.address.state),
            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_14[0]": self._text(case.address.zip_code),

            "topmostSubform[0].Page1[0].c1_5[1]": "/2",

            "topmostSubform[0].Page1[0].f1_32[0]": self._money(w2.wages_box1 if w2 else 0),
            "topmostSubform[0].Page1[0].f1_33[0]": "0",
            "topmostSubform[0].Page1[0].f1_34[0]": "0",
            "topmostSubform[0].Page1[0].f1_35[0]": "0",
            "topmostSubform[0].Page1[0].f1_36[0]": "0",
            "topmostSubform[0].Page1[0].f1_37[0]": "0",
            "topmostSubform[0].Page1[0].f1_38[0]": "0",
            "topmostSubform[0].Page1[0].f1_39[0]": "0",
            "topmostSubform[0].Page1[0].f1_40[0]": "",
            "topmostSubform[0].Page1[0].f1_41[0]": self._money(w2.wages_box1 if w2 else 0),
            "topmostSubform[0].Page1[0].f1_42[0]": "0",
            "topmostSubform[0].Page1[0].f1_43[0]": self._money(interest.taxable_interest if interest else 0),
            "topmostSubform[0].Page1[0].f1_44[0]": self._money(dividends.qualified_dividends if dividends else 0),
            "topmostSubform[0].Page1[0].f1_45[0]": self._money(dividends.ordinary_dividends if dividends else 0),
            "topmostSubform[0].Page1[0].f1_46[0]": "0",
            "topmostSubform[0].Page1[0].f1_47[0]": "0",
            "topmostSubform[0].Page1[0].f1_48[0]": "0",
            "topmostSubform[0].Page1[0].f1_49[0]": "0",
            "topmostSubform[0].Page1[0].f1_50[0]": "0",
            "topmostSubform[0].Page1[0].f1_51[0]": "0",
            "topmostSubform[0].Page1[0].f1_52[0]": "0",
            "topmostSubform[0].Page1[0].f1_53[0]": self._money(schedule_c.net_profit if schedule_c else 0),
            "topmostSubform[0].Page1[0].f1_54[0]": self._money(federal.total_income),
            "topmostSubform[0].Page1[0].f1_55[0]": self._money(federal.adjustments),
            "topmostSubform[0].Page1[0].f1_56[0]": self._money(federal.agi),
            "topmostSubform[0].Page1[0].f1_57[0]": self._money(federal.standard_deduction),
            "topmostSubform[0].Page1[0].f1_58[0]": self._money(federal.qbi_deduction),
            "topmostSubform[0].Page1[0].f1_59[0]": self._money(federal.standard_deduction + federal.qbi_deduction),
            "topmostSubform[0].Page1[0].f1_60[0]": self._money(federal.taxable_income),

            "topmostSubform[0].Page2[0].f2_02[0]": self._money(federal.tax_before_credits),
            "topmostSubform[0].Page2[0].f2_03[0]": "0",
            "topmostSubform[0].Page2[0].f2_04[0]": self._money(federal.tax_before_credits),
            "topmostSubform[0].Page2[0].f2_05[0]": self._money(federal.child_tax_credit),
            "topmostSubform[0].Page2[0].f2_06[0]": "0",
            "topmostSubform[0].Page2[0].f2_07[0]": self._money(federal.child_tax_credit),
            "topmostSubform[0].Page2[0].f2_08[0]": self._money(max(federal.tax_before_credits - federal.child_tax_credit, 0)),
            "topmostSubform[0].Page2[0].f2_09[0]": self._money(federal.self_employment_tax),
            "topmostSubform[0].Page2[0].f2_10[0]": self._money(federal.total_tax),
            "topmostSubform[0].Page2[0].f2_11[0]": self._money(w2.federal_withholding if w2 else 0),
            "topmostSubform[0].Page2[0].f2_12[0]": "0",
            "topmostSubform[0].Page2[0].f2_13[0]": "0",
            "topmostSubform[0].Page2[0].f2_14[0]": self._money(w2.federal_withholding if w2 else 0),
            "topmostSubform[0].Page2[0].f2_15[0]": "0",
            "topmostSubform[0].Page2[0].f2_16[0]": "0",
            "topmostSubform[0].Page2[0].f2_17[0]": "0",
            "topmostSubform[0].Page2[0].f2_18[0]": "0",
            "topmostSubform[0].Page2[0].f2_19[0]": "0",
            "topmostSubform[0].Page2[0].f2_20[0]": "0",
            "topmostSubform[0].Page2[0].f2_21[0]": "0",
            "topmostSubform[0].Page2[0].f2_22[0]": self._money(federal.total_payments),
            "topmostSubform[0].Page2[0].f2_23[0]": self._money(federal.refund),
            "topmostSubform[0].Page2[0].f2_24[0]": self._money(federal.refund),
            "topmostSubform[0].Page2[0].f2_27[0]": "0",
            "topmostSubform[0].Page2[0].f2_28[0]": self._money(federal.balance_due),
            "topmostSubform[0].Page2[0].f2_29[0]": "0",

            "topmostSubform[0].Page2[0].f2_33[0]": self._text(case.taxpayer.occupation),
            "topmostSubform[0].Page2[0].f2_35[0]": self._text(case.spouse.occupation if case.spouse else ""),
        }

        values.update(self._status_checkbox(case))
        values.update(self._dependent_fields(case))
        return values

    def _overlay_signature_block(self, input_pdf: Path, output_pdf: Path, case: TaxCase) -> None:
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.setFont("Helvetica", 8)

        c.drawString(92, 304, case.taxpayer.full_name)
        c.drawString(274, 304, self._signature_date(case.tax_year))

        if case.spouse:
            c.drawString(92, 274, case.spouse.full_name)
            c.drawString(274, 274, self._signature_date(case.tax_year))

        c.save()
        packet.seek(0)

        base_reader = PdfReader(str(input_pdf))
        overlay_reader = PdfReader(packet)
        writer = PdfWriter()

        for idx, page in enumerate(base_reader.pages):
            if idx == 1:
                page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        with output_pdf.open("wb") as f:
            writer.write(f)

    def split_output_pages(self, combined_pdf: Path, page1_path: Path, page2_path: Path) -> None:
        reader = PdfReader(str(combined_pdf))

        writer1 = PdfWriter()
        writer1.add_page(reader.pages[0])

        writer2 = PdfWriter()
        writer2.add_page(reader.pages[1])

        with page1_path.open("wb") as f:
            writer1.write(f)

        with page2_path.open("wb") as f:
            writer2.write(f)

    def fill(self, output_path: Path, case: TaxCase) -> None:
        field_values = self.build_field_values(case)
        temp_output = output_path.with_name(output_path.stem + "_raw.pdf")

        self.form_filler.fill_form(
            template_path=self.template_path,
            output_path=temp_output,
            field_values=field_values,
        )

        self._overlay_signature_block(temp_output, output_path, case)
        temp_output.unlink(missing_ok=True)