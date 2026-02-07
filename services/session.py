import streamlit as st
from datetime import datetime


def init_session_state():
    current_year = datetime.now().year

    defaults = {
        "access_token": None,
        "refresh_token": None,
        "expires_at": None,
        "dashboard_ready": False,
        "selected_year": current_year,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
