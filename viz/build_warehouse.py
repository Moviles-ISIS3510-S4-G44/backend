from pathlib import Path

import duckdb
import pandas as pd
from sqlalchemy import text
from sqlmodel import Session

from src.marketplace_andes_backend.db import get_engine


RAW_TABLES = [
    "user",
    "university",
    "program",
    "category",
    "listing",
    "listing_status_history",
    "marketplace_transaction",
    "message_thread",
    "message",
    "review",
    "search_event",
    "user_activity_event",
]


def fetch_table(table_name: str, session: Session | None = None) -> pd.DataFrame:
    query = text(f'SELECT * FROM "{table_name}"')
    if session is not None:
        dataframe = pd.read_sql_query(query, session.connection())
        return dataframe

    engine = get_engine()
    with engine.connect() as connection:
        dataframe = pd.read_sql_query(query, connection)
    return dataframe


def load_raw_tables(
    connection: duckdb.DuckDBPyConnection, session: Session | None = None
) -> None:
    for table_name in RAW_TABLES:
        dataframe = fetch_table(table_name, session=session)
        connection.register(f"{table_name}_df", dataframe)
        connection.execute(f"DROP TABLE IF EXISTS raw_{table_name}")
        connection.execute(
            f"CREATE TABLE raw_{table_name} AS SELECT * FROM {table_name}_df"
        )
        connection.unregister(f"{table_name}_df")


def build_dimensions(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_date AS
        WITH timestamps AS (
            SELECT CAST(created_at AS TIMESTAMP) AS ts FROM raw_listing
            UNION ALL
            SELECT CAST(created_at AS TIMESTAMP) AS ts FROM raw_marketplace_transaction
            UNION ALL
            SELECT CAST(completed_at AS TIMESTAMP) AS ts FROM raw_marketplace_transaction WHERE completed_at IS NOT NULL
            UNION ALL
            SELECT CAST(cancelled_at AS TIMESTAMP) AS ts FROM raw_marketplace_transaction WHERE cancelled_at IS NOT NULL
            UNION ALL
            SELECT CAST(created_at AS TIMESTAMP) AS ts FROM raw_message
            UNION ALL
            SELECT CAST(created_at AS TIMESTAMP) AS ts FROM raw_review
            UNION ALL
            SELECT CAST(created_at AS TIMESTAMP) AS ts FROM raw_search_event
            UNION ALL
            SELECT CAST(created_at AS TIMESTAMP) AS ts FROM raw_user_activity_event
        ), bounds AS (
            SELECT MIN(CAST(ts AS DATE)) AS min_date, MAX(CAST(ts AS DATE)) AS max_date
            FROM timestamps
        )
        SELECT
            CAST(strftime(day_value, '%Y%m%d') AS INTEGER) AS date_key,
            day_value AS full_date,
            year(day_value) AS year,
            quarter(day_value) AS quarter,
            month(day_value) AS month,
            day(day_value) AS day,
            isodow(day_value) AS weekday,
            isodow(day_value) IN (6, 7) AS is_weekend
        FROM bounds, generate_series(min_date, max_date, INTERVAL 1 DAY) AS dates(day_value)
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_university AS
        SELECT
            id AS university_id,
            name,
            country,
            city,
            created_at
        FROM raw_university
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_program AS
        SELECT
            id AS program_id,
            university_id,
            name,
            faculty,
            created_at
        FROM raw_program
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_user AS
        SELECT
            u.id AS user_id,
            u.university_id,
            u.program_id,
            split_part(CAST(u.email AS VARCHAR), '@', 2) AS email_domain,
            u.is_verified,
            CAST(u.created_at AS DATE) AS user_created_date,
            u.rating AS current_rating,
            u.name,
            u.email,
            u.last_login_at
        FROM raw_user AS u
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_category AS
        SELECT
            c.id AS category_id,
            c.parent_category_id,
            CAST(c.name AS VARCHAR) AS category_name,
            CAST(p.name AS VARCHAR) AS parent_category_name,
            CASE
                WHEN p.name IS NULL THEN CAST(c.name AS VARCHAR)
                ELSE CAST(p.name AS VARCHAR) || ' > ' || CAST(c.name AS VARCHAR)
            END AS category_path,
            c.is_active,
            c.created_at
        FROM raw_category AS c
        LEFT JOIN raw_category AS p ON c.parent_category_id = p.id
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_listing AS
        SELECT
            id AS listing_id,
            seller_id AS seller_user_id,
            category_id,
            product_type,
            condition,
            is_digital,
            is_negotiable,
            campus_pickup_point,
            created_at,
            published_at,
            status,
            title
        FROM raw_listing
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_transaction_status AS
        SELECT * FROM (
            VALUES
                ('pending', FALSE, FALSE),
                ('completed', TRUE, FALSE),
                ('cancelled', FALSE, TRUE)
        ) AS statuses(status, is_completed, is_cancelled)
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_activity_type AS
        SELECT DISTINCT
            event_type AS activity_type,
            CASE
                WHEN event_type = 'login' THEN 'authentication'
                WHEN event_type IN ('message', 'search') THEN 'engagement'
                ELSE 'commerce'
            END AS activity_group
        FROM raw_user_activity_event
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_message_channel AS
        SELECT 'marketplace_thread' AS channel_name
        """
    )


def build_facts(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_listings AS
        SELECT
            l.id AS listing_fact_key,
            l.id AS listing_id,
            l.seller_id,
            u.university_id,
            l.category_id,
            CAST(strftime(CAST(l.created_at AS DATE), '%Y%m%d') AS INTEGER) AS created_date_key,
            l.price AS listed_price,
            l.status AS listing_status,
            l.quantity_available,
            1 AS created_listing_count
        FROM raw_listing AS l
        LEFT JOIN raw_user AS u ON l.seller_id = u.id
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_transactions AS
        SELECT
            t.id AS transaction_fact_key,
            t.id AS transaction_id,
            t.listing_id,
            t.buyer_id,
            t.seller_id,
            seller.university_id,
            listing.category_id,
            CAST(strftime(CAST(t.created_at AS DATE), '%Y%m%d') AS INTEGER) AS transaction_date_key,
            t.status AS transaction_status,
            t.listed_price,
            t.agreed_price,
            CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END AS completion_count,
            CASE WHEN t.status = 'cancelled' THEN 1 ELSE 0 END AS cancellation_count,
            CASE
                WHEN t.completed_at IS NULL THEN NULL
                ELSE datediff(
                    'hour',
                    CAST(listing.created_at AS TIMESTAMP),
                    CAST(t.completed_at AS TIMESTAMP)
                )
            END AS time_to_sell_hours
        FROM raw_marketplace_transaction AS t
        LEFT JOIN raw_listing AS listing ON t.listing_id = listing.id
        LEFT JOIN raw_user AS seller ON t.seller_id = seller.id
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_listing_daily_snapshot AS
        WITH listing_dates AS (
            SELECT
                MIN(CAST(CAST(created_at AS TIMESTAMP) AS DATE)) AS min_date,
                MAX(
                    CAST(
                        COALESCE(
                            CAST(sold_at AS TIMESTAMP),
                            CAST(archived_at AS TIMESTAMP),
                            CAST(created_at AS TIMESTAMP)
                        ) AS DATE
                    )
                ) AS max_date
            FROM raw_listing
        ), snapshot_dates AS (
            SELECT day_value AS snapshot_date
            FROM listing_dates, generate_series(min_date, max_date, INTERVAL 1 DAY) AS dates(day_value)
        )
        SELECT
            CAST(l.id AS VARCHAR) || '-' || CAST(snapshot_date AS VARCHAR) AS listing_snapshot_fact_key,
            l.id AS listing_id,
            l.seller_id,
            u.university_id,
            l.category_id,
            CAST(strftime(snapshot_date, '%Y%m%d') AS INTEGER) AS snapshot_date_key,
            snapshot_date >= CAST(CAST(l.created_at AS TIMESTAMP) AS DATE)
                AND (l.sold_at IS NULL OR snapshot_date <= CAST(CAST(l.sold_at AS TIMESTAMP) AS DATE))
                AND (l.archived_at IS NULL OR snapshot_date <= CAST(CAST(l.archived_at AS TIMESTAMP) AS DATE)) AS is_active,
            l.sold_at IS NOT NULL
                AND snapshot_date >= CAST(CAST(l.sold_at AS TIMESTAMP) AS DATE) AS is_sold,
            l.quantity_available > 0 AS is_available,
            l.price AS listed_price
        FROM raw_listing AS l
        LEFT JOIN raw_user AS u ON l.seller_id = u.id
        CROSS JOIN snapshot_dates
        WHERE snapshot_date >= CAST(CAST(l.created_at AS TIMESTAMP) AS DATE)
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_user_activity AS
        SELECT
            a.id AS user_activity_fact_key,
            a.id AS activity_event_id,
            CAST(strftime(CAST(a.created_at AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
            a.user_id,
            u.university_id,
            a.listing_id,
            a.event_type AS activity_type,
            1 AS activity_count
        FROM raw_user_activity_event AS a
        LEFT JOIN raw_user AS u ON a.user_id = u.id
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_search_events AS
        SELECT
            s.id AS search_fact_key,
            s.id AS search_event_id,
            CAST(strftime(CAST(s.created_at AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
            s.user_id,
            u.university_id,
            s.category_id,
            s.query_text,
            s.results_count,
            1 AS search_count
        FROM raw_search_event AS s
        LEFT JOIN raw_user AS u ON s.user_id = u.id
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_messages AS
        SELECT
            m.id AS message_fact_key,
            m.id AS message_id,
            CAST(strftime(CAST(m.created_at AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
            thread.listing_id,
            thread.buyer_id,
            thread.seller_id,
            'marketplace_thread' AS message_channel,
            1 AS message_count
        FROM raw_message AS m
        LEFT JOIN raw_message_thread AS thread ON m.thread_id = thread.id
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_reviews AS
        SELECT
            r.id AS review_fact_key,
            r.id AS review_id,
            CAST(strftime(CAST(r.created_at AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
            r.transaction_id,
            r.reviewee_id AS seller_user_id,
            r.reviewer_id AS reviewer_user_id,
            reviewee.university_id,
            r.rating AS rating_value,
            1 AS review_count
        FROM raw_review AS r
        LEFT JOIN raw_user AS reviewee ON r.reviewee_id = reviewee.id
        """
    )


def build_metric_views(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_gmv_by_day AS
        SELECT
            d.full_date,
            COALESCE(SUM(f.agreed_price), 0) AS gmv
        FROM dim_date AS d
        LEFT JOIN fact_transactions AS f
            ON d.date_key = f.transaction_date_key
            AND f.transaction_status = 'completed'
        GROUP BY d.full_date
        ORDER BY d.full_date
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_conversion_rate AS
        SELECT
            d.full_date,
            CASE
                WHEN COUNT(DISTINCT l.listing_id) = 0 THEN 0
                ELSE COUNT(DISTINCT CASE WHEN t.transaction_status = 'completed' THEN t.listing_id END)::DOUBLE
                    / COUNT(DISTINCT l.listing_id)
            END AS conversion_rate
        FROM dim_date AS d
        LEFT JOIN fact_listings AS l ON d.date_key = l.created_date_key
        LEFT JOIN fact_transactions AS t ON d.date_key = t.transaction_date_key
        GROUP BY d.full_date
        ORDER BY d.full_date
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_time_to_sell AS
        SELECT
            d.full_date,
            AVG(time_to_sell_hours) AS avg_time_to_sell_hours
        FROM dim_date AS d
        LEFT JOIN fact_transactions AS f
            ON d.date_key = f.transaction_date_key
            AND f.transaction_status = 'completed'
        GROUP BY d.full_date
        ORDER BY d.full_date
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_active_listings AS
        SELECT
            d.full_date,
            COUNT(DISTINCT CASE WHEN s.is_active THEN s.listing_id END) AS active_listings
        FROM dim_date AS d
        LEFT JOIN fact_listing_daily_snapshot AS s ON d.date_key = s.snapshot_date_key
        GROUP BY d.full_date
        ORDER BY d.full_date
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_dau_mau AS
        SELECT
            d.full_date,
            COUNT(DISTINCT CASE WHEN a.date_key = d.date_key THEN a.user_id END) AS dau,
            (
                SELECT COUNT(DISTINCT user_id)
                FROM fact_user_activity AS rolling
                WHERE rolling.date_key BETWEEN CAST(strftime(d.full_date - INTERVAL 29 DAY, '%Y%m%d') AS INTEGER)
                    AND d.date_key
            ) AS mau
        FROM dim_date AS d
        LEFT JOIN fact_user_activity AS a ON d.date_key = a.date_key
        GROUP BY d.full_date, d.date_key
        ORDER BY d.full_date
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_supply_vs_demand AS
        SELECT
            c.category_name,
            COUNT(DISTINCT l.listing_id) AS listings_created,
            COUNT(DISTINCT CASE WHEN t.transaction_status = 'completed' THEN t.transaction_id END) AS listings_sold
        FROM dim_category AS c
        LEFT JOIN fact_listings AS l ON c.category_id = l.category_id
        LEFT JOIN fact_transactions AS t ON c.category_id = t.category_id
        GROUP BY c.category_name
        ORDER BY c.category_name
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_most_searched_categories AS
        SELECT
            COALESCE(c.category_name, 'unknown') AS category_name,
            SUM(search_count) AS search_count
        FROM fact_search_events AS s
        LEFT JOIN dim_category AS c ON s.category_id = c.category_id
        GROUP BY COALESCE(c.category_name, 'unknown')
        ORDER BY search_count DESC, category_name
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_price_distribution AS
        SELECT
            c.category_name,
            MIN(l.listed_price) AS min_price,
            MAX(l.listed_price) AS max_price,
            median(l.listed_price) AS median_price,
            quantile_cont(l.listed_price, 0.75) AS p75_price,
            quantile_cont(l.listed_price, 0.90) AS p90_price
        FROM fact_listings AS l
        LEFT JOIN dim_category AS c ON l.category_id = c.category_id
        GROUP BY c.category_name
        ORDER BY c.category_name
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_average_rating AS
        SELECT
            seller_user_id,
            AVG(rating_value) AS average_rating
        FROM fact_reviews
        GROUP BY seller_user_id
        ORDER BY seller_user_id
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_cancel_rate AS
        SELECT
            CASE
                WHEN COUNT(*) = 0 THEN 0
                ELSE SUM(cancellation_count)::DOUBLE / COUNT(*)
            END AS cancel_rate
        FROM fact_transactions
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE VIEW metric_messages_per_sale AS
        SELECT
            CASE
                WHEN completed_sales = 0 THEN 0
                ELSE total_messages::DOUBLE / completed_sales
            END AS messages_per_sale
        FROM (
            SELECT
                COUNT(*) AS total_messages,
                (
                    SELECT COUNT(*)
                    FROM fact_transactions
                    WHERE transaction_status = 'completed'
                ) AS completed_sales
            FROM fact_messages
        ) AS base
        """
    )


def build_warehouse(
    database_path: Path | None = None, session: Session | None = None
) -> Path:
    output_path = database_path or Path("viz/output/analytics.duckdb")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(output_path))
    try:
        load_raw_tables(connection, session=session)
        build_dimensions(connection)
        build_facts(connection)
        build_metric_views(connection)
    finally:
        connection.close()
    return output_path


if __name__ == "__main__":
    build_warehouse()
