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
