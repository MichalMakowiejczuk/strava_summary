import pandas as pd
import datetime as dt
from typing import Optional, Literal
from itertools import product

from services.constants import MONTHS_MAP, DAYS


def process_heatmap_day_month(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["start_datetime_local"] = pd.to_datetime(df["start_datetime_local"])

    heatmap_df = df.groupby(["month", "day_name"]).size().reset_index(name="count")

    # --- months x days ---
    MONTHS = list(range(1, 13))  # 1..12
    full_index = pd.DataFrame(
        list(product(MONTHS, DAYS)), columns=["month", "day_name"]
    )
    heatmap_df = full_index.merge(
        heatmap_df, on=["month", "day_name"], how="left"
    ).fillna(0)
    heatmap_df["count"] = heatmap_df["count"].astype(int)
    heatmap_df["day_name"] = pd.Categorical(
        heatmap_df["day_name"], categories=DAYS, ordered=True
    )
    heatmap_df["month_str"] = heatmap_df["month"].apply(
        lambda x: MONTHS_MAP.get(x, "Unknown")
    )
    heatmap_df = heatmap_df.sort_values(["month", "day_name"]).reset_index(drop=True)

    return heatmap_df


def process_data_histogram(
    df: pd.DataFrame, col: str, bins: tuple | int = 10
) -> pd.DataFrame:
    """
    Generate a DataFrame suitable for plotting a histogram.
    Returns columns: bin, label, count
    """
    df = df.copy()

    # --- metrics configuration ---
    METRICS = {
        "elapsed_time": {"unit": "min", "scale": 1 / 60, "decimals": 0},
        "distance_km": {"unit": "km", "scale": 1.0, "decimals": 0},
        "elevation_gain_m": {"unit": "m", "scale": 1.0, "decimals": 0},
    }

    metric = METRICS.get(col)
    if metric is None:
        raise ValueError(f"Unsupported metric: {col}")

    # --- normalization ---
    df[col] = df[col] * metric["scale"]

    # --- bins ---
    if isinstance(bins, int):
        bins_edges = pd.interval_range(
            start=df[col].min(), end=df[col].max(), periods=bins
        )
    else:
        bins_edges = pd.IntervalIndex.from_breaks(bins, closed="left")

    col_bins = pd.cut(df[col], bins=bins_edges)

    histogram = (
        col_bins.value_counts().sort_index().rename("count").reset_index(name="count")
    )

    histogram = histogram.rename(columns={histogram.columns[0]: "bin"})

    def format_label(interval: pd.Interval) -> str:
        left = interval.left
        right = interval.right
        decimals = metric["decimals"]

        def fmt(x, unit):
            if x == float("inf"):
                return "∞"
            return f"{x:.{decimals}f} {unit}"

        if metric["unit"] == "min":
            # conversion into hours if > 60
            if right > 60:
                left_val = left / 60
                right_val = right / 60
                unit = "h"
            else:
                left_val = left
                right_val = right
                unit = "min"
        else:
            left_val = left
            right_val = right
            unit = metric["unit"]

        if right == float("inf"):
            return f"{fmt(left_val, unit)}+"

        return f"{fmt(left_val, unit)} – {fmt(right_val, unit)}"

    histogram["label"] = histogram["bin"].apply(format_label)

    return histogram


def process_time_data(
    df: pd.DataFrame,
    freq: Literal["day_name", "month", "weekend", "week", "daypart"] = "month",
    col: Optional[str] = None,
    agg: Literal["sum", "count", "nunique"] = "count",
    result_name: Optional[str] = None,
) -> pd.DataFrame:
    df = df.copy()
    df["month_str"] = df["month"].apply(lambda x: MONTHS_MAP.get(x, "Unknown"))

    # --- define grouping ---
    if freq == "day_name":
        group_col = "day_name"
        order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
    elif freq == "weekend":
        group_col = "is_weekend"
        order = ["Weekday", "Weekend"]
    elif freq == "month":
        group_col = "month_str"
        order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
    elif freq == "week":
        group_col = "week"

        year = df["year"].iloc[0]  # one year data
        last_week = dt.date(year, 12, 28).isocalendar().week

        order = list(range(1, last_week + 1))
    elif freq == "daypart":
        group_col = "daypart"
        order = ["Morning", "Afternoon", "Evening", "Night"]
    else:
        raise ValueError(f"Unsupported freq: {freq}")

    # --- aggregation ---
    if agg == "sum":
        if col is None:
            raise ValueError("Column must be specified for sum aggregation")
        aggregated = df.groupby(group_col)[col].sum().reset_index()
    elif agg == "count":
        aggregated = (
            df.groupby(group_col).size().reset_index(name=result_name or "count")
        )
    elif agg == "nunique":
        if col is None:
            raise ValueError("Column must be specified for nunique aggregation")
        aggregated = (
            df.groupby(group_col)[col]
            .nunique()
            .reset_index(name=result_name or "count")
        )
    else:
        raise ValueError(f"Unsupported aggregation: {agg}")

    # --- reorder ---
    aggregated = (
        aggregated.set_index(group_col).reindex(order, fill_value=0).reset_index()
    )

    # --- rename aggregated column if specified ---
    if result_name and result_name not in aggregated.columns:
        aggregated = aggregated.rename(columns={aggregated.columns[1]: result_name})

    num_cols = aggregated.select_dtypes(include="number").columns
    aggregated[num_cols] = aggregated[num_cols].round(0).astype(int)

    return aggregated
