from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter


class PDFFormFiller:
    def list_fields(self, pdf_path: Path) -> dict[str, Any]:
        reader = PdfReader(str(pdf_path))
        fields = reader.get_fields()
        return fields or {}

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

        writer.update_page_form_field_values(
            writer.pages,
            field_values,
            auto_regenerate=False,
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as f:
            writer.write(f)