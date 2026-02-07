import streamlit as st


from components.sidebar import sidebar
from services.session import init_session_state
from services.strava_api.client import StravaClient

from services.filters.ui import apply_activity_filters
from services.distance_bins import get_distance_bins

from components.tabs import (
    overview,
    training_patterns,
    monthly_stats,
    weekly_stats,
    activity_distribution,
)


st.set_page_config(page_title="Strava Dashboard", layout="wide")
st.title("Strava Yearly Dashboard")

# --- INIT ---
init_session_state()
sidebar()

if not st.session_state.dashboard_ready:
    st.info("Select year and generate your dashboard")
    st.stop()

year = st.session_state.selected_year
client = StravaClient()

# --- LOAD DATA ---
with st.spinner("Downloading activities..."):
    df = client.get_activities(year)

# --- FILTERS ---
df, selected_sport = apply_activity_filters(df)

if df.empty:
    st.info("No activities for selected filters, try different options")
    st.stop()

# --- DOMAIN LOGIC ---
distance_bins = get_distance_bins(selected_sport)

# --- TABS ---
tabs = st.tabs(
    [
        "Overview",
        "Training patterns",
        "Monthly Stats",
        "Weekly Stats",
        "Activity Distribution",
    ]
)

overview.render(tabs[0], df, year)
training_patterns.render(tabs[1], df)
monthly_stats.render(tabs[2], df)
weekly_stats.render(tabs[3], df)
activity_distribution.render(tabs[4], df, distance_bins)
