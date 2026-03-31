from pathlib import Path
from typing import Annotated

from analytics import user_retention_viz


import typer

OUT_DIR = Path("out")

app = typer.Typer(help="Visualize To-Do App analytics")

PathOption = Annotated[
    Path,
    typer.Option(
        "--db",
        help="Path to the DuckDB analytics file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
]


@app.command()
def visualize(
    db_path: PathOption,
):
    user_retention_viz(db_path, OUT_DIR)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    app()


if __name__ == "__main__":
    main()
