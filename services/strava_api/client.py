import os
import time
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

from services.data_processing import process_activities_data

AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
BASE_URL = "https://www.strava.com/api/v3"


class StravaClient:
    def __init__(self):
        self.client_id = os.getenv("STRAVA_CLIENT_ID")
        self.client_secret = os.getenv("STRAVA_CLIENT_SECRET")
        self.redirect_uri = os.getenv("STRAVA_REDIRECT_URI")

    # ---------- AUTH ----------

    def get_auth_url(self) -> str:
        return (
            f"{AUTH_URL}"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&approval_prompt=force"
            f"&scope=read,activity:read_all"
        )

    def exchange_code(self, code: str):
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        self._store_tokens(response.json())

    def refresh_token(self):
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": st.session_state.refresh_token,
            },
        )
        response.raise_for_status()
        self._store_tokens(response.json())

    def logout(self):
        if "access_token" in st.session_state:
            requests.post(
                f"{BASE_URL}/oauth/deauthorize",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            )

        for key in ("access_token", "refresh_token", "expires_at", "dashboard_ready"):
            st.session_state[key] = None
        st.cache_data.clear()

    # ---------- TOKEN HANDLING ----------

    def _store_tokens(self, data: dict):
        st.session_state.access_token = data["access_token"]
        st.session_state.refresh_token = data["refresh_token"]
        st.session_state.expires_at = data["expires_at"]

    def _get_valid_access_token(self):
        if not st.session_state.access_token:
            raise RuntimeError("User not authenticated")

        if not st.session_state.expires_at:
            return st.session_state.access_token

        if time.time() >= st.session_state.expires_at:
            self._refresh_token()

        return st.session_state.access_token

    # ---------- API ----------

    def get_athlete(self) -> dict:
        token = self._get_valid_access_token()

        response = requests.get(
            f"{BASE_URL}/athlete",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

    # ---------- ACTIVITIES ----------

    def get_activities(self, year: int) -> pd.DataFrame:
        token = self._get_valid_access_token()
        athlete_id = self.get_athlete()["id"]
        return self._get_activities_cached(year, athlete_id, token)

    @staticmethod
    @st.cache_data(ttl=3600)
    def _get_activities_cached(
        year: int,
        athlete_id: int,
        token: str,
    ) -> pd.DataFrame:
        """
        Cache per (athlete_id, year)
        """
        after = int(datetime(year, 1, 1).timestamp())
        before = int(datetime(year + 1, 1, 1).timestamp())

        activities = []
        page = 1

        while True:
            response = requests.get(
                f"{BASE_URL}/athlete/activities",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "after": after,
                    "before": before,
                    "per_page": 200,
                    "page": page,
                },
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            if not data:
                break

            activities.extend(data)
            page += 1

        df = pd.DataFrame(activities)
        return process_activities_data(df)
