from pathlib import Path

from pypdf import PdfReader


def main() -> None:
    pdf_path = Path("templates/pdf/federal/form_1040.pdf")
    reader = PdfReader(str(pdf_path))
    fields = reader.get_fields() or {}

    for name, meta in fields.items():
        print("=" * 80)
        print(f"FIELD: {name}")
        print(meta)


if __name__ == "__main__":
    main()