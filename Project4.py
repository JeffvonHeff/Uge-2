import pandas as pd
import matplotlib.pyplot as plt


def load_housing_data(csv_path: str = "DKHousingPricesSample100k.csv") -> pd.DataFrame:
    """Read the housing dataset and ensure purchase prices are numeric."""
    df = pd.read_csv(csv_path)
    df["purchase_price"] = pd.to_numeric(df["purchase_price"], errors="coerce")
    return df


def summarize_by_region(df: pd.DataFrame) -> pd.Series:
    """Average purchase price per region, sorted from highest to lowest."""
    return (
        df.groupby("region", dropna=False)["purchase_price"]
        .mean()
        .sort_values(ascending=False)
        .rename("avg_purchase_price")
    )


def summarize_by_house_type(df: pd.DataFrame) -> pd.DataFrame:
    """Average purchase price and listing count per housing type, sorted by price."""
    return (
        df.groupby("house_type", dropna=False)
        .agg(
            avg_purchase_price=("purchase_price", "mean"),
            listing_count=("house_id", "count"),
        )
        .sort_values("avg_purchase_price", ascending=False)
    )


def plot_grouped_results(region_avg: pd.Series, type_summary: pd.DataFrame) -> None:
    """Visualize region and house-type summaries with matplotlib."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    region_avg.plot(kind="bar", ax=axes[0], color="steelblue")
    axes[0].set_title("Average Purchase Price by Region")
    axes[0].set_ylabel("DKK")
    axes[0].tick_params(axis="x", rotation=45, labelrotation=45)

    type_summary["avg_purchase_price"].plot(kind="bar", ax=axes[1], color="coral")
    axes[1].set_title("Average Purchase Price by Housing Type")
    axes[1].set_ylabel("DKK")
    axes[1].tick_params(axis="x", rotation=45, labelrotation=45)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    data = load_housing_data()
    region_average = summarize_by_region(data)
    house_type_summary = summarize_by_house_type(data)

    print("Average purchase price by region:\n", region_average, "\n")
    print("Average purchase price by housing type:\n", house_type_summary, "\n")

    plot_grouped_results(region_average, house_type_summary)
