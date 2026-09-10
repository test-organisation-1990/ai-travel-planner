import time

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Wait between our own requests so we don't hit Overpass too frequently.
_last_request_time = 0
MIN_REQUEST_INTERVAL = 5


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    reraise=True,
)
def _call_overpass(query: str):

    global _last_request_time

    # Simple rate limiting
    elapsed = time.time() - _last_request_time

    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)

    headers = {
        "User-Agent": "TripPlannerAI/1.0"
    }

    response = httpx.post(
        OVERPASS_URL,
        data={"data": query},
        headers=headers,
        timeout=60,
    )

    _last_request_time = time.time()

    response.raise_for_status()

    return response.json()


def find_pois(latitude: float, longitude: float) -> list[dict]:

    query = f"""
    [out:json];
    (
      node["tourism"](around:10000,{latitude},{longitude});
      way["tourism"](around:10000,{latitude},{longitude});
      relation["tourism"](around:10000,{latitude},{longitude});
    );
    out center;
    """

    data = _call_overpass(query)

    pois = []

    for element in data.get("elements", []):

        tags = element.get("tags", {})
        name = tags.get("name:en")

        if not name:
            continue

        if element["type"] == "node":

            lat = element.get("lat")
            lon = element.get("lon")

        else:

            center = element.get("center", {})

            lat = center.get("lat")
            lon = center.get("lon")

        if lat is None or lon is None:
            continue

        pois.append({
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "type": tags.get("tourism", "unknown"),
        })

    return pois