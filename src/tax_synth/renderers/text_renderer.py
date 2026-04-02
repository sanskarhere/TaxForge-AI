from pathlib import Path

from tax_synth.models.case import TaxCase
from tax_synth.renderers.jinja_env import build_jinja_env


class TextRenderer:
    def __init__(self, templates_root: Path) -> None:
        self.templates_root = templates_root
        self.env = build_jinja_env(templates_root)

    def render_template(self, template_name: str, case: TaxCase) -> str:
        template = self.env.get_template(template_name)
        rendered = template.render(case=case.model_dump(mode="json"))

        print(f"[DEBUG] templates_root = {self.templates_root}")
        print(f"[DEBUG] template_name = {template_name}")
        print(f"[DEBUG] rendered_length = {len(rendered)}")

        return rendered