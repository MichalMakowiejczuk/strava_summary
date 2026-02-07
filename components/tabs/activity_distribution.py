import streamlit as st

from services.charts_data import process_data_histogram
from components.charts import render_bar_chart


def render(tab, df, distance_bins):
    """
    Activity distribution:
    - time
    - distance
    - elevation gain
    """
    with tab:
        st.subheader("Time")

        time_hist_df = process_data_histogram(
            df,
            col="elapsed_time",
            bins=(0, 60, 120, 300, 600, float("inf")),
        )

        render_bar_chart(
            time_hist_df,
            x_col="label",
            y_col="count",
            x_title="Duration Intervals",
            y_title="Number of Activities",
            height=200,
        )

        st.subheader("Distance")

        distance_hist_df = process_data_histogram(
            df,
            col="distance_km",
            bins=distance_bins,
        )

        render_bar_chart(
            distance_hist_df,
            x_col="label",
            y_col="count",
            x_title="Distance Intervals",
            y_title="Number of Activities",
            height=200,
        )

        st.subheader("Elevation Gain")

        elevation_hist_df = process_data_histogram(
            df,
            col="elevation_gain_m",
            bins=(0, 100, 500, 1000, 2000, float("inf")),
        )

        render_bar_chart(
            elevation_hist_df,
            x_col="label",
            y_col="count",
            x_title="Elevation Intervals",
            y_title="Number of Activities",
            height=200,
        )
