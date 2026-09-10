from Common.state import TravelState

def validate_errors(state: TravelState):

    if state.get("error"):
        return "error"

    return "success"