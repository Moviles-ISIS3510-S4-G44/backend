from pathlib import Path

import duckdb
from sqlmodel import Session

from viz.build_warehouse import build_warehouse
from viz.generate_charts import generate_charts
from viz.sample_data import seed_sample_data


def test_viz_pipeline_builds_duckdb_and_charts(session: Session, tmp_path: Path):
    seed_sample_data(session=session)

    database_path = tmp_path / "analytics.duckdb"
    charts_path = tmp_path / "charts"

    built_database = build_warehouse(database_path=database_path, session=session)
    output_files = generate_charts(database_path=built_database, charts_path=charts_path)

    assert built_database.exists()
    assert all(path.exists() for path in output_files)
    assert len(output_files) >= 6

    connection = duckdb.connect(str(built_database), read_only=True)
    try:
        fact_transaction_row = connection.execute(
            "SELECT COUNT(*) FROM fact_transactions"
        ).fetchone()
        fact_listing_row = connection.execute(
            "SELECT COUNT(*) FROM fact_listings"
        ).fetchone()
        category_row = connection.execute(
            "SELECT COUNT(*) FROM metric_most_searched_categories"
        ).fetchone()
        messages_per_sale_row = connection.execute(
            "SELECT messages_per_sale FROM metric_messages_per_sale"
        ).fetchone()
        date_row = connection.execute(
            "SELECT COUNT(*) FROM dim_date"
        ).fetchone()
    finally:
        connection.close()

    assert fact_transaction_row is not None
    assert fact_listing_row is not None
    assert category_row is not None
    assert messages_per_sale_row is not None
    assert date_row is not None

    fact_transaction_count = fact_transaction_row[0]
    fact_listing_count = fact_listing_row[0]
    category_count = category_row[0]
    messages_per_sale = messages_per_sale_row[0]
    date_count = date_row[0]

    assert fact_listing_count >= 30
    assert fact_transaction_count >= 30
    assert category_count >= 6
    assert date_count >= 30
    assert messages_per_sale > 0
