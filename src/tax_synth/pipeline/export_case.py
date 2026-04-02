from __future__ import annotations

from pathlib import Path

import orjson

from tax_synth.models.case import TaxCase
from tax_synth.renderers.pdf_renderer import PDFRenderer
from tax_synth.renderers.text_renderer import TextRenderer


def export_case(case: TaxCase, output_dir: Path, templates_root: Path) -> None:
    case_dir = output_dir / case.case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    # Save structured JSON
    json_path = case_dir / "case_data.json"
    json_path.write_bytes(
        orjson.dumps(case.model_dump(mode="json"), option=orjson.OPT_INDENT_2)
    )

    # ---------- TEXT / MARKDOWN OUTPUT ----------
    text_renderer = TextRenderer(templates_root / "text")

    client_summary_md = text_renderer.render_template("client_summary.md.j2", case)
    prompt_md = text_renderer.render_template("prompt.md.j2", case)
    executive_summary_md = text_renderer.render_template("executive_summary.md.j2", case)
    completed_forms_summary_md = text_renderer.render_template("completed_forms_summary.md.j2", case)

    (case_dir / "client_summary.md").write_text(client_summary_md, encoding="utf-8")
    (case_dir / "prompt.md").write_text(prompt_md, encoding="utf-8")
    (case_dir / "executive_summary.md").write_text(executive_summary_md, encoding="utf-8")
    (case_dir / "completed_forms_summary.md").write_text(
        completed_forms_summary_md, encoding="utf-8"
    )

    # ---------- PDF OUTPUT ----------
    pdf_renderer = PDFRenderer()

    pdf_renderer.render_text_to_pdf(
        text_content=client_summary_md,
        output_path=case_dir / "client_summary.pdf",
        title="Client Summary",
    )

    pdf_renderer.render_text_to_pdf(
        text_content=prompt_md,
        output_path=case_dir / "prompt.pdf",
        title="Prompt Data",
    )

    pdf_renderer.render_text_to_pdf(
        text_content=executive_summary_md,
        output_path=case_dir / "executive_summary.pdf",
        title="Executive Summary",
    )

    pdf_renderer.render_text_to_pdf(
        text_content=completed_forms_summary_md,
        output_path=case_dir / "completed_forms_summary.pdf",
        title="Completed Forms Summary",
    )