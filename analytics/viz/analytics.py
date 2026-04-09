from pathlib import Path


import duckdb
import matplotlib.pyplot as plt


def user_retention_viz(db_path: Path, out_dir: Path):
    conn = duckdb.connect(db_path)

    query = """
        SELECT
            current_status,
            SUM(is_new_user) as new_users,
            SUM(is_recent_churn) as churned_users,
            SUM(user_count) as total_count
        FROM marketplace_andes_analytics.fact_user_stats
        GROUP BY current_status
    """
    df = conn.execute(query).df()
    conn.close()

    output_path = out_dir / "user_retention_viz.png"

    _, (pie_ax, bar_ax) = plt.subplots(1, 2, figsize=(14, 6))

    pie_ax.pie(
        df["total_count"],
        labels=df["current_status"],
        autopct="%1.1f%%",
    )
    pie_ax.set_title("Current User Status Distribution")

    metrics = ["New (30d)", "Churned (30d)"]
    values = [df["new_users"].sum(), df["churned_users"].sum()]
    bar_ax.bar(metrics, values)
    bar_ax.set_title("User Volatility (Last 30 Days)")
    bar_ax.set_ylabel("Number of Users")

    plt.tight_layout()
    plt.savefig(output_path, dpi=600, bbox_inches="tight")
    plt.close()


def listing_publish_time_viz(db_path: Path, out_dir: Path):
    conn = duckdb.connect(db_path)

    query = """
        SELECT
            avg_minutes_to_publish,
            median_minutes_to_publish,
            min_minutes_to_publish,
            max_minutes_to_publish,
            published_listing_count
        FROM marketplace_andes_analytics.avg_time_to_publish
    """
    df = conn.execute(query).df()
    conn.close()

    output_path = out_dir / "listing_publish_time_viz.png"

    _, (bar_ax, count_ax) = plt.subplots(1, 2, figsize=(14, 6))

    metrics = ["Avg", "Median", "Min", "Max"]
    values = [
        df["avg_minutes_to_publish"].iloc[0],
        df["median_minutes_to_publish"].iloc[0],
        df["min_minutes_to_publish"].iloc[0],
        df["max_minutes_to_publish"].iloc[0],
    ]
    bar_ax.bar(metrics, values, color=["steelblue", "orange", "green", "red"])
    bar_ax.set_title("Time to Publish a Listing (minutes)")
    bar_ax.set_ylabel("Minutes")

    count_ax.bar(["Published Listings"], [df["published_listing_count"].iloc[0]], color="steelblue")
    count_ax.set_title("Published Listing Count")
    count_ax.set_ylabel("Count")

    plt.tight_layout()
    plt.savefig(output_path, dpi=600, bbox_inches="tight")
    plt.close()
