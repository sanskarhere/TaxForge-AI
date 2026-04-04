from __future__ import annotations

from pathlib import Path
from pathlib import Path
from pypdf import PdfReader, PdfWriter


def merge_pdfs(input_paths: list[Path], output_path: Path) -> None:
    writer = PdfWriter()

    for pdf_path in input_paths:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            writer.add_page(page)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        writer.write(f)