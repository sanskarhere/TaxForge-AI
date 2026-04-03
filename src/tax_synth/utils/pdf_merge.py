from pathlib import Path

from pypdf import PdfWriter


def merge_pdfs(pdf_paths: list[Path], output_path: Path) -> None:
    writer = PdfWriter()

    for pdf_path in pdf_paths:
        writer.append(str(pdf_path))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        writer.write(f)