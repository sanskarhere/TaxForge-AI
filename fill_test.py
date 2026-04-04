from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject

input_pdf = Path("templates/pdf/federal/form_1040.pdf")
output_pdf = Path("filled_1040.pdf")

reader = PdfReader(str(input_pdf))
writer = PdfWriter()

# copy all pages
for page in reader.pages:
    writer.add_page(page)

# IMPORTANT: copy AcroForm from reader to writer
if "/AcroForm" in reader.trailer["/Root"]:
    writer._root_object.update(
        {
            NameObject("/AcroForm"): reader.trailer["/Root"]["/AcroForm"]
        }
    )

    # ensure appearances are regenerated
    writer._root_object["/AcroForm"].update(
        {NameObject("/NeedAppearances"): BooleanObject(True)}
    )
else:
    print("No AcroForm found in source PDF")
    raise SystemExit

# sample test data
data_page1 = {
    "topmostSubform[0].Page1[0].f1_01[0]": "John",
    "topmostSubform[0].Page1[0].f1_02[0]": "Doe",
    "topmostSubform[0].Page1[0].f1_03[0]": "123-45-6789",
    "topmostSubform[0].Page1[0].f1_07[0]": "123 Main Street",
    "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_10[0]": "Austin",
    "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_11[0]": "TX",
    "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_12[0]": "78704",
    "topmostSubform[0].Page1[0].f1_32[0]": "50000",
    "topmostSubform[0].Page1[0].f1_57[0]": "50000",
    "topmostSubform[0].Page1[0].f1_59[0]": "50000",
}

data_page2 = {
    "topmostSubform[0].Page2[0].f2_01[0]": "5000",
    "topmostSubform[0].Page2[0].f2_09[0]": "4500",
    "topmostSubform[0].Page2[0].f2_18[0]": "4500",
    "topmostSubform[0].Page2[0].f2_19[0]": "500",
}

# fill page 1
writer.update_page_form_field_values(writer.pages[0], data_page1)

# fill page 2
writer.update_page_form_field_values(writer.pages[1], data_page2)

# save
with open(output_pdf, "wb") as f:
    writer.write(f)

print("DONE: filled_1040.pdf created")