from pathlib import Path

from viz.build_warehouse import build_warehouse
from viz.generate_charts import generate_charts
from viz.sample_data import seed_sample_data


def run_pipeline() -> tuple[Path, list[Path]]:
    seed_sample_data()
    database_path = build_warehouse()
    chart_paths = generate_charts(database_path=database_path)
    return database_path, chart_paths


if __name__ == "__main__":
    run_pipeline()
