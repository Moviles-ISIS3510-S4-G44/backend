from pathlib import Path

import duckdb

from viz.build_warehouse import build_warehouse
from viz.generate_charts import generate_charts
from viz.sample_data import seed_sample_data


METRIC_EXPORTS = {
    "metric_best_reputation_students": "best_reputation_students.csv",
    "metric_most_viewed_products_week": "most_viewed_products_week.csv",
    "metric_average_listing_publish_time": "average_listing_publish_time.csv",
    "metric_listing_creation_failure_rate": "listing_creation_failure_rate.csv",
    "metric_user_top_categories": "user_top_categories.csv",
    "metric_user_interest_summary": "user_interest_summary.csv",
    "metric_posts_created_last_week": "posts_created_last_week.csv",
}


def export_metric_views(
    database_path: Path, output_path: Path | None = None
) -> list[Path]:
    export_dir = output_path or Path("viz/output/answers")
    export_dir.mkdir(parents=True, exist_ok=True)

    exported_files: list[Path] = []
    connection = duckdb.connect(str(database_path), read_only=True)
    try:
        for view_name, file_name in METRIC_EXPORTS.items():
            dataframe = connection.execute(f"SELECT * FROM {view_name}").df()
            file_path = export_dir / file_name
            dataframe.to_csv(file_path, index=False)
            exported_files.append(file_path)
    finally:
        connection.close()

    return exported_files


def run_pipeline() -> tuple[Path, list[Path], list[Path]]:
    seed_sample_data()
    database_path = build_warehouse()
    chart_paths = generate_charts(database_path=database_path)
    export_paths = export_metric_views(database_path=database_path)
    return database_path, chart_paths, export_paths


if __name__ == "__main__":
    database_path, chart_paths, export_paths = run_pipeline()
    print(f"Analytics warehouse: {database_path}")
    print("Charts:")
    for chart_path in chart_paths:
        print(f"- {chart_path}")
    print("Answer exports:")
    for export_path in export_paths:
        print(f"- {export_path}")
