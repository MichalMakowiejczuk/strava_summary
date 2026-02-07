import streamlit as st
from services.metrics_data import process_metrics_data
from components.metrics import render_metric


def render(tab, df, year: int):
    with tab:
        st.subheader(f"Summary for {year}")
        metrics_data = process_metrics_data(df)

        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric("Total Activities", metrics_data["total_activities"])
            render_metric("Total Active Days", metrics_data["total_active_days"])

        with col2:
            render_metric("Favorite Sport", metrics_data["favorite_sport"])
            render_metric("Favorite Workout Day", metrics_data["favorite_day"])

        with col3:
            render_metric("Longest Daily Streak", metrics_data["best_daily_streak"])
            render_metric("Longest Weekly Streak", metrics_data["best_weekly_streak"])

        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Time")
            render_metric(
                "Total Time",
                metrics_data["total_time_hms"],
                f"Total duration (elapsed time) of all activities in {year}.",
            )
            render_metric(
                "Best Activity",
                metrics_data["max_time_hms"],
                "Total duration (elapsed time) of the longest activity.",
            )
            render_metric(
                "Best Week",
                metrics_data["best_weekly_time_hms"],
                "Total duration (elapsed time) of all activities in one week.",
            )
        with col2:
            st.header("Distance")
            render_metric(
                "Total Distance (km)",
                metrics_data["total_distance_km"],
                f"Total distance covered in {year}.",
            )
            render_metric(
                "Best Activity",
                metrics_data["max_distance_km"],
                "Total distance covered in one activity.",
            )
            render_metric("Best Week", metrics_data["best_weekly_distance_km"])
            render_metric(
                "Around the World 🌍", f"{metrics_data['percent_around_world']:.2f}%"
            )
        with col3:
            st.header("Climbing")
            render_metric(
                "Total Elevation gain",
                metrics_data["total_elevation_gain_m"],
                f"Total elevation gain of all activities in {year}.",
            )
            render_metric(
                "Best Activity",
                metrics_data["max_elevation_gain_m"],
                "Total elevation gain in one activity.",
            )
            render_metric("Best Week", metrics_data["best_weekly_elevation_gain_m"])
            render_metric(
                "Mount Everest Climbed 🌄", f"{metrics_data['x_everest']:.2f}× up"
            )
        with col4:
            st.header("Social")
            render_metric("Total Strava Kudos", metrics_data["total_kudos"])
            render_metric("Total Activity Companions", metrics_data["total_athletes"])
            render_metric("Total Comments", metrics_data["total_comments"])
        tab.markdown("---")
