import altair as alt
import streamlit as st
import pandas as pd


from components.constants import MONTH_LABELS, DAY_ORDER


def render_weekday_month_heatmap(df):
    chart = (
        alt.Chart(df)
        .mark_circle(opacity=0.85)
        .encode(
            x=alt.X(
                "month_str:N", sort=MONTH_LABELS, title="", axis=alt.Axis(labelAngle=0)
            ),
            y=alt.Y("day_name:N", sort=DAY_ORDER, title=""),
            size=alt.Size("count:Q", scale=alt.Scale(range=[0, 600]), legend=None),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=[
                alt.Tooltip("month_str:N", title="Month"),
                alt.Tooltip("day_name:N", title="Weekday"),
                alt.Tooltip("count:Q", title="Number of activities"),
            ],
        )
        .properties(height=250)
    )

    st.altair_chart(chart, use_container_width=True)


def render_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_title: str = "",
    y_title: str = "",
    x_tooltip: str = "",
    y_tooltip: str = "",
    orientation: str = "vertical",
    height: int = 250,
):
    orientation = orientation.lower()
    if orientation not in {"vertical", "horizontal"}:
        raise ValueError("orientation must be 'vertical' or 'horizontal'")

    df = df.copy()

    if orientation == "vertical":
        x = alt.X(
            f"{x_col}:O",
            sort=df[x_col].tolist(),
            title=x_title,
            axis=alt.Axis(labelAngle=0),
        )
        y = alt.Y(f"{y_col}:Q", title=y_title)
    else:
        x = alt.X(f"{y_col}:Q", title=y_title, axis=alt.Axis(labelAngle=0))
        y = alt.Y(f"{x_col}:O", sort=df[x_col].tolist(), title=x_title)

    if x_tooltip == "":
        x_tooltip = x_title
    if y_tooltip == "":
        y_tooltip = y_title

    tooltip = [
        alt.Tooltip(f"{x_col}:O", title=x_tooltip),
        alt.Tooltip(f"{y_col}:N", title=y_tooltip),
    ]

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=x,
            y=y,
            tooltip=tooltip,
        )
        .properties(height=height)
    )

    st.altair_chart(chart, use_container_width=True)


def render_pie_chart(df: pd.DataFrame, category_col: str, value_col: str = "count"):
    """
    Render pie chart using Altair.
    """
    chart = (
        alt.Chart(df)
        .mark_arc()
        .encode(
            theta=alt.Theta(f"{value_col}:Q", title="Number of activities"),
            color=alt.Color(f"{category_col}:N", title="Category"),
            tooltip=[
                alt.Tooltip(f"{category_col}:N", title="Category"),
                alt.Tooltip(f"{value_col}:Q", title="Number of activities"),
            ],
        )
        .properties(height=200)
    )
    st.altair_chart(chart, use_container_width=True)


def render_grouped_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    value_cols: list[str],
    x_title: str = "",
    y_title: str = "",
    x_tooltip: str = "",
    y_tooltip: str = "",
    labels: dict[str, str] | None = None,
    data_unit: str = "",
):
    df = df.copy()
    labels = labels or {}
    x_order = df[x_col].tolist()

    # --- wide → long ---
    df_long = df.melt(
        id_vars=[x_col],
        value_vars=value_cols,
        var_name="metric",
        value_name="value",
    )

    df_long["metric_label"] = df_long["metric"].map(labels).fillna(df_long["metric"])

    # --- tooltip fallback ---
    x_tt = x_tooltip or x_title or ""
    y_tt = y_tooltip or y_title or ""

    chart = (
        alt.Chart(df_long)
        .transform_calculate(Duration=f"format(datum.value, ',.0f') + ' {data_unit}'")
        .mark_bar()
        .encode(
            x=alt.X(
                f"{x_col}:O", title=x_title, axis=alt.Axis(labelAngle=0), sort=x_order
            ),
            xOffset=alt.XOffset("metric_label:N"),
            y=alt.Y("value:Q", title=y_title),
            color=alt.Color(
                "metric_label:N", title="", legend=alt.Legend(orient="top")
            ),
            tooltip=[
                alt.Tooltip(f"{x_col}:O", title=x_tt),
                alt.Tooltip("metric_label:N", title="Type"),
                alt.Tooltip("Duration:N", title=y_tt),
            ],
        )
        .properties(height=250, padding={"left": 40, "top": 0})
    )

    st.altair_chart(chart, use_container_width=True)
