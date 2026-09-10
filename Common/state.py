from typing import TypedDict, List, Dict, Any

class POI(TypedDict):
    name: str
    latitude: float
    longitude: float
    type: str

# State
class TravelState(TypedDict):
    user_query: str
    session_id: str
    destination: str
    source: str
    minimum_budget: float
    maximum_budget: float
    destination_latitude: str
    destination_longitude: str
    destination_display_name: str
    overpass_result: List[POI]
    itinerary: List[Dict[str, Any]]
    itinerary_html: str
    wikivoyage_result: str
    fianl_response: str
    chat_id: int
    error: bool
    errorMessage: str