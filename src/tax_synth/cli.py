from pathlib import Path

import typer
from rich.console import Console

from tax_synth.config import settings
from tax_synth.pipeline.build_case import build_one_case
from tax_synth.pipeline.export_case import export_case

app = typer.Typer(help="Synthetic tax dataset generator")
console = Console()


@app.command()
def pilot(
    count: int = typer.Option(5, min=1, help="How many pilot cases to generate"),
    out_dir: str = typer.Option("data/output/pilot", help="Output directory"),
) -> None:
    output_dir = settings.resolved_path(Path(out_dir))
    templates_root = settings.resolved_path(settings.templates_dir)

    for idx in range(1, count + 1):
        case_id = f"CASE_{idx:04d}"
        case = build_one_case(case_id=case_id, seed=settings.random_seed + idx)
        export_case(case, output_dir, templates_root)
        console.print(f"[green]Generated[/green] {case_id}")

    console.print(f"[bold cyan]Done.[/bold cyan] Files written to {output_dir}")


if __name__ == "__main__":
    app()