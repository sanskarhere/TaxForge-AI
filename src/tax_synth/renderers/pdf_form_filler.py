from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


class PDFFormFiller:
    def list_fields(self, pdf_path: Path) -> dict[str, Any]:
        reader = PdfReader(str(pdf_path))
        return reader.get_fields() or {}

    def fill_form(
        self,
        *,
        template_path: Path,
        output_path: Path,
        field_values: dict[str, Any],
    ) -> None:
        reader = PdfReader(str(template_path))
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        root = reader.trailer["/Root"]
        if "/AcroForm" in root:
            writer._root_object.update(
                {
                    NameObject("/AcroForm"): root["/AcroForm"].clone(writer)
                }
            )
            writer._root_object["/AcroForm"].update(
                {
                    NameObject("/NeedAppearances"): BooleanObject(True)
                }
            )

        for page in writer.pages:
            writer.update_page_form_field_values(
                page,
                field_values,
                auto_regenerate=True,
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as f:
            writer.write(f)