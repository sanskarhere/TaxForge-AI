from pathlib import Path
from pypdf import PdfReader

pdf_path = Path("templates/pdf/federal/form_1040.pdf")
reader = PdfReader(str(pdf_path))

fields = reader.get_fields()

if not fields:
    print("NO_FIELDS_FOUND")
else:
    print("FIELDS_FOUND:")
    for key in fields.keys():
        print(key)