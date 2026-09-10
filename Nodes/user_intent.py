import json
from Common.state import TravelState
from Common.Model import llm
import time

def user_intent(state: TravelState):
    
    if llm is None:
        return {
            "error": True,
            "errorMessage": "OpenAI service is currently unavailable. Please configure the API key."
        }
            
    prompt = f"""
    You are an expert travel planner.

    Extract the following information from the user's travel query.

    Return ONLY valid JSON with these fields:

    {{
        "destination": "destination the customer wants to visit",
        "source": "city/place from where the customer wants to travel",
        "minimum_budget": "minimum budget of the customer",
        "maximum_budget": "maximum budget of the customer"
    }}

    Rules:
    - If a value is not provided by the user, return null.
    - Do not guess or invent any value.
    - minimum_budget and maximum_budget should contain numeric values when available.
    - Return only JSON. Do not add explanations or markdown.

    User Query:
    {state["user_query"]}
    """
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)

            # Convert LLM response into Python dictionary
            travel_details = json.loads(response.content)
            
            required_fields = ["destination"]
            
            for field in required_fields:
                if travel_details[field] is None:
                    return {
                        "error": True,
                        "errorMessage": "we are not able to find the destination address of your travel. Please type correct input for processing"
                    }

            return {
                "destination": travel_details["destination"],
                "source": travel_details["source"],
                "minimum_budget": travel_details["minimum_budget"],
                "maximum_budget": travel_details["maximum_budget"]
            }
        except json.JSONDecodeError as e:
            print(
                f"Attempt {attempt + 1}/{max_retries} failed: "
                f"Invalid JSON returned by LLM. Error: {e}"
            )
        except Exception as e:
            print(
                f"Attempt {attempt + 1}/{max_retries} failed: "
                f"{type(e).__name__}: {e}"
            )
            
        # Wait before retrying
        if attempt < max_retries - 1:
            time.sleep(2)
            
        # All retries failed
        print("All retry attempts failed.")
        
        return {
            "destination": None,
            "source": None,
            "minimum_budget": None,
            "maximum_budget": None,
            "error": True,
            "errorMessage": "There is something issue with AI APP. PLease try Later"
        }