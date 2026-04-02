from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


def build_jinja_env(templates_root: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_root)),
        undefined=StrictUndefined,
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )