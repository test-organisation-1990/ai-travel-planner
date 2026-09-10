import httpx
import streamlit as st

NOMINATIM_URL = st.secrets["NOMINATIM_URL"]

@st.cache_data(ttl=86400)
def geocode(destination: str) -> dict:

    params = {
        "q": destination,
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "trip-planner-ai/1.0"
    }

    response = httpx.get(
        NOMINATIM_URL,
        params=params,
        headers=headers,
        timeout=5,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        raise ValueError(f"Location not found: {destination}")

    place = results[0]

    return {
        "latitude": float(place["lat"]),
        "longitude": float(place["lon"]),
        "display_name": place["display_name"],
    }