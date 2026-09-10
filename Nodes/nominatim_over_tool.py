from Common.state import TravelState
from services.nominatim import geocode

def nominatim_over_tool(state: TravelState):
    try:
        geocode_response = geocode(state["destination"])
        return {
                "destination_latitude": geocode_response["latitude"],
                "destination_longitude": geocode_response["longitude"],
                "destination_display_name": geocode_response["display_name"],
            }
    except Exception as e:
        return {
            "error": True,
            "errorMessage": f"Nominatim Services: {e}"
        }
        
    