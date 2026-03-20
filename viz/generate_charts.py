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

    return output_files


if __name__ == "__main__":
    generate_charts()
