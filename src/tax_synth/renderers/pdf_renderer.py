from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class PDFRenderer:
    def render_text_to_pdf(
        self,
        *,
        text_content: str,
        output_path: Path,
        title: str = "Document",
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.fontSize = 18

        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            spaceAfter=8,
        )

        story = [Paragraph(title, title_style), Spacer(1, 12)]

        for line in text_content.split("\n"):
            line = line.strip()

            if not line:
                story.append(Spacer(1, 10))
                continue

            # Markdown cleanup
            if line.startswith("#"):
                clean = line.replace("#", "").strip()
                story.append(Paragraph(f"<b>{escape(clean)}</b>", body_style))

            elif line.startswith("- "):
                clean = line[2:].strip()
                story.append(Paragraph(f"• {escape(clean)}", body_style))

            else:
                story.append(Paragraph(escape(line), body_style))

        doc.build(story)