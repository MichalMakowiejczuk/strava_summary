import pandas as pd
import streamlit as st
from typing import Literal


def format_seconds(seconds: float, format: Literal["hms", "hm", "h"]) -> str:
    """Convert seconds to hours, minutes, seconds format.

    Args:
        seconds (float): Time in seconds.
        format (Literal['hms', 'hm', 'h']): Output format.
    Returns:
        str: Formatted time string.
    """
    format = format.lower()
    total_seconds = int(seconds)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if format == "hms":
        return f"{hours} h {minutes:02} min {secs:02} s"
    elif format == "hm":
        return f"{hours} h {minutes:02} min"
    elif format == "h":
        return f"{hours} h"
    else:
        raise ValueError("Invalid format. Expected one of: 'hms', 'hm', 'h'.")


def format_metric_data(metric_data: float | int, format: Literal["m", "km"]) -> str:
    format = format.lower()
    metric_data = int(metric_data)

    if format == "m":
        return f"{metric_data} m"
    elif format == "km":
        return f"{metric_data} km"
    else:
        raise ValueError("Invalid format. Expected one of: 'm', 'km'.")


@st.cache_data(show_spinner=False, ttl=3600)
def process_metrics_data(df: pd.DataFrame) -> dict:
    """Process metrics data for streamlit app.

    Args:
        df (pd.DataFrame): clean data from strava api.

    Returns:
        dict: Processed metrics data.
    """
    metrics_data = {}

    total_activities = len(df)
    total_active_days = df["start_datetime_local"].dt.date.nunique()
    total_distance_km = df["distance_km"].sum().round(2)
    total_time_hms = format_seconds(df["elapsed_time"].sum(), "h")
    total_elevation_gain_m = int(df["elevation_gain_m"].sum())
    total_kudos = int(df["kudos_count"].sum())
    total_comments = int(df["comment_count"].sum())
    total_athletes = int(df["athlete_count"].sum())

    sport_mode = df["sport_type"].mode()
    favorite_sport = sport_mode[0] if not sport_mode.empty else "N/A"

    day_mode = df["start_datetime_local"].dt.day_name().mode()
    favorite_day = day_mode[0] if not day_mode.empty else "N/A"

    best_weekly_distance_km = (
        df.resample("W", on="start_datetime_local")["distance_km"].sum().max().round(2)
    )
    best_weekly_time_hms = format_seconds(
        df.resample("W", on="start_datetime_local")["elapsed_time"].sum().max(), "h"
    )
    best_weekly_elevation_gain_m = int(
        df.resample("W", on="start_datetime_local")["elevation_gain_m"].sum().max()
    )

    max_distance_km = df["distance_km"].max().round(2)
    max_time_hms = format_seconds(df["elapsed_time"].max(), "hm")
    max_elevation_gain_m = int(df["elevation_gain_m"].max())
    max_kudos = int(df["kudos_count"].max())
    max_comments = int(df["comment_count"].max())

    # streaks calculation
    # daily streaks
    active_days = (
        df[["start_date"]]
        .drop_duplicates()
        .sort_values("start_date")
        .reset_index(drop=True)
    )
    active_days["date"] = pd.to_datetime(active_days["start_date"])
    if len(active_days) == 1:
        active_days["grp"] = active_days["start_date"].iloc[0] - pd.to_timedelta(
            active_days.index[0], unit="D"
        )
    else:
        active_days["grp"] = active_days["start_date"] - pd.to_timedelta(
            active_days.index, unit="D"
        )

    daily_streaks = active_days.groupby("grp").size().reset_index(name="streak_length")

    best_daily_streak = int(daily_streaks["streak_length"].max())

    # weekly streaks
    df["year"] = df["start_datetime_local"].dt.isocalendar().year
    df["week"] = df["start_datetime_local"].dt.isocalendar().week

    active_weeks = (
        df[["year", "week"]]
        .drop_duplicates()
        .sort_values(["year", "week"])
        .reset_index(drop=True)
    )
    active_weeks["week_index"] = active_weeks["year"] * 52 + active_weeks["week"]

    active_weeks["grp"] = active_weeks["week_index"] - active_weeks.index

    weekly_streaks = (
        active_weeks.groupby("grp").size().reset_index(name="streak_length")
    )

    best_weekly_streak = int(weekly_streaks["streak_length"].max())

    # fun facts
    X_everest = total_elevation_gain_m / 8848
    percent_around_world = (total_distance_km / 40075) * 100

    # totals
    metrics_data["total_activities"] = total_activities
    metrics_data["total_active_days"] = total_active_days
    metrics_data["total_distance_km"] = format_metric_data(total_distance_km, "km")
    metrics_data["total_time_hms"] = total_time_hms
    metrics_data["total_elevation_gain_m"] = format_metric_data(
        total_elevation_gain_m, "m"
    )
    metrics_data["total_kudos"] = total_kudos
    metrics_data["total_comments"] = total_comments
    metrics_data["total_athletes"] = total_athletes

    # favorite sport and day
    metrics_data["favorite_sport"] = favorite_sport
    metrics_data["favorite_day"] = favorite_day
    # best weekly
    metrics_data["best_weekly_distance_km"] = format_metric_data(
        best_weekly_distance_km, "km"
    )
    metrics_data["best_weekly_time_hms"] = best_weekly_time_hms
    metrics_data["best_weekly_elevation_gain_m"] = format_metric_data(
        best_weekly_elevation_gain_m, "m"
    )

    # records
    metrics_data["max_distance_km"] = format_metric_data(max_distance_km, "km")
    metrics_data["max_time_hms"] = max_time_hms
    metrics_data["max_elevation_gain_m"] = format_metric_data(max_elevation_gain_m, "m")
    metrics_data["max_kudos"] = max_kudos
    metrics_data["max_comments"] = max_comments

    # streaks
    metrics_data["best_daily_streak"] = best_daily_streak
    metrics_data["best_weekly_streak"] = best_weekly_streak

    # fun facts
    metrics_data["x_everest"] = round(X_everest, 2)
    metrics_data["percent_around_world"] = round(percent_around_world, 2)

    return metrics_data
