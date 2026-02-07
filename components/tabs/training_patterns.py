import streamlit as st

from services.charts_data import (
    process_heatmap_day_month,
    process_time_data,
)

from components.charts import (
    render_weekday_month_heatmap,
    render_bar_chart,
    render_pie_chart,
)


def render(tab, df):
    """
    Training patterns view:
    - weekday vs month heatmap
    - activities per month
    - activities per weekday
    - weekend vs weekday split
    """
    with tab:
        col_left, col_right = st.columns([2, 1])

        # --- LEFT COLUMN ---
        with col_left:
            st.subheader("Training patterns: days vs months")

            heatmap_df = process_heatmap_day_month(df)
            render_weekday_month_heatmap(heatmap_df)

            st.subheader("Number of activities per month")
            monthly_df = process_time_data(df, freq="month", agg="count")
            render_bar_chart(
                monthly_df,
                x_col="month_str",
                y_col="count",
                x_title="Month",
                y_title="Number of activities",
            )

        # --- RIGHT COLUMN ---
        with col_right:
            st.subheader("Activities per weekday")

            weekday_df = process_time_data(df, freq="day_name", agg="count")
            render_bar_chart(
                weekday_df,
                x_col="day_name",
                y_col="count",
                orientation="horizontal",
                x_tooltip="Weekday",
                y_title="Number of activities",
                height=285,
            )

            st.subheader("Weekend vs Weekday Activities")
            weekend_df = process_time_data(df, freq="weekend", agg="count")
            render_pie_chart(
                weekend_df,
                category_col="is_weekend",
                value_col="count",
            )
