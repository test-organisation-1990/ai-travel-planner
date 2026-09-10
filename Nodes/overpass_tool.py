from Common.state import TravelState
from services.overpass import find_pois

def overpass_tool(state: TravelState):
    try:
        overpasss_response = find_pois(state["destination_latitude"], state["destination_longitude"])
                
        return {
            "overpass_result": overpasss_response
        }
    except Exception as e:
        return {
            "error": True,
            "errorMessage": f"Overpass Serives: {e}"
        }