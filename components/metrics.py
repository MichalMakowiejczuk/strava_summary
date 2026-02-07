import streamlit as st


def render_metric(
    title: str, value: str | int | float, help_text: str = "", border: bool = False
):
    """Render a single metric in Streamlit.

    Args:
        title (str): Title of the metric.
        value (str | int | float): Value of the metric.
        help_text (str, optional): Help text for the metric. Defaults to "".
    """
    if help_text:
        st.metric(label=title, value=value, delta=None, help=help_text, border=border)
    else:
        st.metric(label=title, value=value, delta=None, border=border)
