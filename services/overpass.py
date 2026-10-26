import time
import httpx

from tenacity import retry, stop_after_attempt, wait_exponential


# Primary + fallback Overpass endpoints
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


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

    last_error = None

    for overpass_url in OVERPASS_URLS:

        try:

            response = httpx.post(
                overpass_url,
                data={"data": query},
                headers=headers,
                timeout=150,
            )

            _last_request_time = time.time()

            response.raise_for_status()

            return response.json()

        except (httpx.ConnectError, httpx.ConnectTimeout) as e:

            last_error = e
            continue

    raise last_error


def find_pois(latitude: float, longitude: float) -> list[dict]:

    query = f"""
        [out:json][timeout:120];

        (
            node(around:12000,{latitude},{longitude})["tourism"];
            way(around:12000,{latitude},{longitude})["tourism"];
            relation(around:12000,{latitude},{longitude})["tourism"];

            node(around:12000,{latitude},{longitude})
                ["natural"~"beach|waterfall|peak|cave|spring"];

            way(around:12000,{latitude},{longitude})
                ["natural"~"beach|waterfall|peak|cave|spring"];

            node(around:12000,{latitude},{longitude})
                ["historic"~"monument|castle|fort|archaeological_site"];

            way(around:12000,{latitude},{longitude})
                ["historic"~"monument|castle|fort|archaeological_site"];

            node(around:12000,{latitude},{longitude})
                ["leisure"~"park|garden|nature_reserve"];

            way(around:12000,{latitude},{longitude})
                ["leisure"~"park|garden|nature_reserve"];
        );

        out center tags;
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