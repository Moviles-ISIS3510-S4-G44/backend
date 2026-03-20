from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


def _save_line_chart(dataset, x_key: str, y_key: str, title: str, output_path: Path) -> None:
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.plot(dataset[x_key], dataset[y_key], marker="o")
    axis.set_title(title)
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)


def _save_bar_chart(dataset, x_key: str, y_key: str, title: str, output_path: Path) -> None:
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(dataset[x_key], dataset[y_key])
    axis.set_title(title)
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)


def _save_horizontal_bar_chart(
    dataset, x_key: str, y_key: str, title: str, output_path: Path
) -> None:
    figure, axis = plt.subplots(figsize=(10, 7))
    axis.barh(dataset[y_key], dataset[x_key])
    axis.set_title(title)
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)


def _save_single_value_chart(label: str, value: float, title: str, output_path: Path) -> None:
    figure, axis = plt.subplots(figsize=(7, 5))
    bars = axis.bar([label], [value])
    axis.set_title(title)
    axis.tick_params(axis="x", rotation=20)
    bar = bars[0]
    axis.text(
        bar.get_x() + bar.get_width() / 2,
        value,
        f"{value:.2f}",
        ha="center",
        va="bottom",
    )
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)


def generate_charts(database_path: Path | None = None, charts_path: Path | None = None) -> list[Path]:
    duckdb_path = database_path or Path("viz/output/analytics.duckdb")
    output_dir = charts_path or Path("viz/output/charts")
    output_dir.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(duckdb_path), read_only=True)
    try:
        gmv = connection.execute("SELECT * FROM metric_gmv_by_day").df()
        conversion = connection.execute("SELECT * FROM metric_conversion_rate").df()
        active = connection.execute("SELECT * FROM metric_active_listings").df()
        dau_mau = connection.execute("SELECT * FROM metric_dau_mau").df()
        searched = connection.execute(
            "SELECT * FROM metric_most_searched_categories"
        ).df()
        supply_vs_demand = connection.execute(
            "SELECT * FROM metric_supply_vs_demand"
        ).df()
        best_reputation = connection.execute(
            "SELECT * FROM metric_best_reputation_students"
        ).df()
        most_viewed = connection.execute(
            "SELECT * FROM metric_most_viewed_products_week"
        ).df()
        publish_time = connection.execute(
            "SELECT * FROM metric_average_listing_publish_time"
        ).df()
        creation_failure_rate = connection.execute(
            "SELECT * FROM metric_listing_creation_failure_rate"
        ).df()
        user_top_categories = connection.execute(
            "SELECT * FROM metric_user_top_categories"
        ).df()
        user_interest_summary = connection.execute(
            "SELECT * FROM metric_user_interest_summary"
        ).df()
        posts_created_last_week = connection.execute(
            "SELECT * FROM metric_posts_created_last_week"
        ).df()
    finally:
        connection.close()

    output_files: list[Path] = []

    gmv_path = output_dir / "gmv_by_day.png"
    _save_line_chart(gmv, "full_date", "gmv", "GMV by Day", gmv_path)
    output_files.append(gmv_path)

    conversion_path = output_dir / "conversion_rate.png"
    _save_line_chart(
        conversion,
        "full_date",
        "conversion_rate",
        "Conversion Rate by Day",
        conversion_path,
    )
    output_files.append(conversion_path)

    active_path = output_dir / "active_listings.png"
    _save_line_chart(
        active,
        "full_date",
        "active_listings",
        "Active Listings by Day",
        active_path,
    )
    output_files.append(active_path)

    dau_path = output_dir / "dau_vs_mau.png"
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.plot(dau_mau["full_date"], dau_mau["dau"], marker="o", label="DAU")
    axis.plot(dau_mau["full_date"], dau_mau["mau"], marker="o", label="MAU")
    axis.set_title("DAU vs MAU")
    axis.legend()
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(dau_path)
    plt.close(figure)
    output_files.append(dau_path)

    searched_path = output_dir / "most_searched_categories.png"
    _save_bar_chart(
        searched,
        "category_name",
        "search_count",
        "Most Searched Categories",
        searched_path,
    )
    output_files.append(searched_path)

    supply_path = output_dir / "supply_vs_demand.png"
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(supply_vs_demand["category_name"], supply_vs_demand["listings_created"], label="Created")
    axis.bar(supply_vs_demand["category_name"], supply_vs_demand["listings_sold"], label="Sold", alpha=0.8)
    axis.set_title("Listings Created vs Sold per Category")
    axis.legend()
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(supply_path)
    plt.close(figure)
    output_files.append(supply_path)

    best_reputation_path = output_dir / "best_reputation_students.png"
    best_reputation_chart = best_reputation.head(10).copy()
    _save_horizontal_bar_chart(
        best_reputation_chart,
        "reputation_score",
        "name",
        "Best Reputation Students",
        best_reputation_path,
    )
    output_files.append(best_reputation_path)

    most_viewed_path = output_dir / "most_viewed_products_week.png"
    _save_bar_chart(
        most_viewed,
        "title",
        "view_count",
        "Most Viewed Products of the Week",
        most_viewed_path,
    )
    output_files.append(most_viewed_path)

    publish_time_path = output_dir / "average_listing_publish_time.png"
    average_minutes_to_publish = (
        float(publish_time["average_minutes_to_publish"].iloc[0])
        if not publish_time.empty
        else 0.0
    )
    _save_single_value_chart(
        "Avg Minutes",
        average_minutes_to_publish,
        "Average Time to Publish a Listing",
        publish_time_path,
    )
    output_files.append(publish_time_path)

    failure_rate_path = output_dir / "listing_creation_failure_rate.png"
    figure, axis = plt.subplots(figsize=(8, 5))
    failure_counts = creation_failure_rate.iloc[0] if not creation_failure_rate.empty else None
    total_attempts = int(failure_counts["total_attempts"]) if failure_counts is not None else 0
    failed_attempts = int(failure_counts["failed_attempts"]) if failure_counts is not None else 0
    failure_percentage = (
        float(failure_counts["failure_percentage"]) if failure_counts is not None else 0.0
    )
    labels = ["Attempts", "System Failures"]
    values = [total_attempts, failed_attempts]
    axis.bar(labels, values)
    axis.set_title("Listing Creation Attempts vs System Failures")
    axis.text(
        0.5,
        max(values) if max(values) > 0 else 0,
        f"Failure rate: {failure_percentage:.2f}%",
        ha="center",
        va="bottom",
    )
    figure.tight_layout()
    figure.savefig(failure_rate_path)
    plt.close(figure)
    output_files.append(failure_rate_path)

    user_top_categories_path = output_dir / "user_top_categories.png"
    top_user_category_scores = user_top_categories.copy()
    top_user_category_scores["user_category"] = (
        top_user_category_scores["name"] + " - " + top_user_category_scores["category_name"]
    )
    if not top_user_category_scores.empty:
        top_user_category_scores = top_user_category_scores.sort_values(
            by="interest_score", ascending=False
        ).head(15)
    _save_horizontal_bar_chart(
        top_user_category_scores,
        "interest_score",
        "user_category",
        "Top User Category Affinities",
        user_top_categories_path,
    )
    output_files.append(user_top_categories_path)

    user_interest_summary_path = output_dir / "user_interest_summary.png"
    interest_summary_counts = user_interest_summary.groupby(
        "top_category", as_index=False
    ).agg(user_count=("user_id", "count"))
    if interest_summary_counts.empty:
        interest_summary_counts["user_count"] = []
    else:
        interest_summary_counts = interest_summary_counts.sort_values(
            by="user_count", ascending=False
        )
    _save_bar_chart(
        interest_summary_counts,
        "top_category",
        "user_count",
        "Most Common Inferred User Interests",
        user_interest_summary_path,
    )
    output_files.append(user_interest_summary_path)

    posts_created_last_week_path = output_dir / "posts_created_last_week.png"
    _save_bar_chart(
        posts_created_last_week,
        "full_date",
        "posts_created",
        "Posts Created per Day in the Last Week",
        posts_created_last_week_path,
    )
    output_files.append(posts_created_last_week_path)

    return output_files


if __name__ == "__main__":
    generate_charts()
