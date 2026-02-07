import streamlit as st
from datetime import datetime
from services.strava_api.client import StravaClient
from components.constants import about


def sidebar():
    client = StravaClient()
    query_params = st.query_params

    # --- OAuth callback ---
    if "code" in query_params:
        if not st.session_state.access_token:
            client.exchange_code(query_params["code"])

        st.query_params.clear()
        st.rerun()

    with st.sidebar:
        if not st.session_state.access_token:
            st.info(about)
            if st.button("Authorize Strava"):
                url = client.get_auth_url()
                st.markdown(
                    f"""<meta http-equiv="refresh" content="0; url={url}">""",
                    unsafe_allow_html=True,
                )
            st.stop()

        if st.session_state.access_token is not None:
            athlete = client.get_athlete()
            st.success(f"Welcome, {athlete['firstname']} {athlete['lastname']}!")
            main_container = st.container()
            with main_container:
                left, right = st.columns(2)
            with left:
                st.image(athlete.get("profile"), width=124)
            with right:
                with st.popover("INFO", use_container_width=True):
                    st.write(about)

                if st.button("Logout", use_container_width=True):
                    client.logout()
                    st.rerun()

            st.markdown("---")
            st.header("Settings")

            current_year = datetime.now().year
            options = list(range(2010, current_year + 1))
            st.selectbox(
                "Choose Year:",
                options=options,
                key="selected_year",
            )

            if st.button("Generate dashboard", use_container_width=True):
                st.session_state.dashboard_ready = True
