import streamlit as st

from services.charts_data import process_time_data
from components.charts import (
    render_bar_chart,
    render_grouped_bar_chart,
)


def render(tab, df):
    """
    Weekly statistics:
    - time (moving vs elapsed)
    - distance
    - elevation gain
    """
    with tab:
        st.subheader("Weekly Time")

        time_df = process_time_data(
            df,
            freq="week",
            col=["moving_time_h", "elapsed_time_h"],
            agg="sum",
        )

        render_grouped_bar_chart(
            time_df,
            x_col="week",
            value_cols=["moving_time_h", "elapsed_time_h"],
            x_title="Week",
            y_title="Time (h)",
            labels={
                "elapsed_time_h": "Elapsed Time",
                "moving_time_h": "Moving Time",
            },
            data_unit="h",
        )

        st.subheader("Weekly Distance")

        distance_df = process_time_data(
            df,
            freq="week",
            col="distance_km",
            agg="sum",
            result_name="total_distance_km",
        )

        render_bar_chart(
            distance_df,
            x_col="week",
            y_col="total_distance_km",
            x_title="Week",
            y_title="Total Distance (km)",
        )

        st.subheader("Weekly Elevation Gain")

        elevation_df = process_time_data(
            df,
            freq="week",
            col="elevation_gain_m",
            agg="sum",
            result_name="total_elevation_gain_m",
        )

        render_bar_chart(
            elevation_df,
            x_col="week",
            y_col="total_elevation_gain_m",
            x_title="Week",
            y_title="Total Elevation Gain (m)",
        )
