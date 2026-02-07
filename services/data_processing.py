import pandas as pd
import numpy as np

from services.constants import SPORT_CATEGORY_MAP


def process_activities_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process Strava-like activities dataframe.

    Cleans data, creates features, and converts units.

    Args:
        df (pd.DataFrame): raw activity dataframe with columns like
            'distance', 'moving_time', 'sport_type', etc.

    Returns:
        pd.DataFrame: processed dataframe with additional columns:
            - sport_category (categorical)
            - distance_km
            - average_speed_kmh
            - year, month, day, day_name, weekday, start_hour
            - is_weekend, daypart
    """

    if df.empty:
        return df

    cols_to_keep = [
        "distance",
        "moving_time",
        "elapsed_time",
        "total_elevation_gain",
        "sport_type",
        "start_date_local",
        "kudos_count",
        "comment_count",
        "athlete_count",
    ]

    df = df.reindex(columns=cols_to_keep)

    # Data cleaning
    df["start_datetime_local"] = pd.to_datetime(df["start_date_local"])
    df["start_date"] = df["start_datetime_local"].dt.date
    df["sport_category"] = pd.Categorical(
        df["sport_type"].map(SPORT_CATEGORY_MAP).fillna("Other")
    )
    df["sport_type"] = pd.Categorical(df["sport_type"])
    df["distance_km"] = df["distance"] / 1000
    df["elevation_gain_m"] = df["total_elevation_gain"]
    df["athlete_count"] = df["athlete_count"] - 1  # exclude self

    # sort by date
    df = df.sort_values(by="start_date_local").reset_index(drop=True)

    # Feature engineering
    df["year"] = df["start_datetime_local"].dt.year
    df["month"] = df["start_datetime_local"].dt.month
    df["day"] = df["start_datetime_local"].dt.day
    df["day_name"] = df["start_datetime_local"].dt.day_name()
    df["weekday"] = df["start_datetime_local"].dt.weekday
    df["week"] = df["start_datetime_local"].dt.isocalendar().week
    df["start_hour"] = df["start_datetime_local"].dt.hour
    df["is_weekend"] = df["weekday"].isin([5, 6])
    df["is_weekend"] = df["is_weekend"].map({True: "Weekend", False: "Weekday"})
    df["elapsed_time_h"] = (df["elapsed_time"] + 1800) // 3600  # 5h 40min -> 6h
    df["moving_time_h"] = (df["moving_time"] + 1800) // 3600

    conditions = [
        (df["start_hour"] >= 5) & (df["start_hour"] < 12),
        (df["start_hour"] >= 12) & (df["start_hour"] < 17),
        (df["start_hour"] >= 17) & (df["start_hour"] < 21),
    ]
    choices = ["Morning", "Afternoon", "Evening"]
    df["daypart"] = np.select(conditions, choices, default="Night")

    # Remove temporary column
    df = df.drop(columns=["distance", "total_elevation_gain", "start_date_local"])

    return df
