from Common.state import TravelState, POI
from Common.Model import llm
from history.database_history import save_chat

import json


def itenatanory_tool(state: TravelState):

    prompt = f"""
You are an expert travel planner.

Create a 4-day travel itinerary based ONLY on the information provided below.

User Request:
{state["user_query"]}

Destination:
{state["destination"]}

Source:
{state["source"]}

Available tourist places from OpenStreetMap:
{state["overpass_result"]}

Wikivoyage travel information:
{state["wikivoyage_result"]}


IMPORTANT RULES FOR ITINERARY:

1. Select places ONLY from the OpenStreetMap POI list.
2. Do not invent any places.
3. Use the exact POI name from the OpenStreetMap data.
4. Organize the selected places across 4 days.
5. For each day, arrange places in a sensible visiting order.
6. Use only "Morning", "Afternoon", or "Evening" for block.
7. Use order starting from 1 for each day.
8. Use Wikivoyage information to help create the description and reason for visiting.
9. Do not generate latitude or longitude.
10. Do not generate any information that is not available from the provided data.
11. Return ONLY valid JSON.
12. Do not return markdown outside the JSON.
13. Do not add explanations outside the JSON.


HTML RULES:

Generate a human-friendly HTML version of the same itinerary.

1. The HTML must contain the complete 4-day itinerary.
2. The HTML must contain the same places as the JSON itinerary.
3. Do not add any places that are not in the JSON itinerary.
4. Do not generate latitude or longitude.
5. Use clean HTML only.
6. Do not use <html>, <head>, or <body>.
7. Start with a <div>.
8. Create a separate section for each day.
9. Show the day as a heading.
10. Group places by Morning, Afternoon, and Evening.
11. Show the place name prominently.
12. Show the description.
13. Show why the place is worth visiting.
14. Use simple language that a normal traveler can understand.
15. Do not generate JavaScript.
16. Do not use <script>, <iframe>, onclick, or other event handlers.
17. Use only safe HTML elements such as:
    div, h2, h3, h4, p, ul, li, strong, span.
18. Do not use markdown inside the HTML.


Return JSON in EXACTLY this structure:

{{
    "itinerary": [
        {{
            "day": 1,
            "block": "Morning",
            "order": 1,
            "name": "Exact POI name",
            "description": "Short and simple description",
            "why_visit": "Why this place is worth visiting"
        }},
        {{
            "day": 1,
            "block": "Afternoon",
            "order": 2,
            "name": "Exact POI name",
            "description": "Short and simple description",
            "why_visit": "Why this place is worth visiting"
        }}
    ],

    "html": "<div class='itinerary'>...</div>"
}}

Remember:

- Return ONLY JSON.
- The JSON must be valid.
- The HTML must be inside the "html" field.
- Do not wrap the response in ```json.
"""


    # Call LLM
    response = llm.invoke(prompt)

    # Get LLM response
    response_content = response.content

    # Convert response to Python dictionary
    try:
        result = json.loads(response_content)

    except json.JSONDecodeError as e:

        print("Invalid JSON returned by LLM:")
        print(response_content)

        return {
            "itinerary": [],
            "itinerary_html": "",
            "error": True,
            "errorMessage": "The travel planner returned an invalid response."
        }


    # Get structured itinerary
    itinerary = result.get("itinerary", [])

    # Get HTML
    itinerary_html = result.get("html", "")


    # Validate that itinerary exists
    if not itinerary:

        return {
            "itinerary": [],
            "itinerary_html": itinerary_html,
            "error": True,
            "errorMessage": "Unable to create the travel itinerary."
        }


    # Save chat
    chat_id = save_chat(
        state["session_id"],
        state["user_query"],
        itinerary
    )

    final_itinary = attach_poi_coordinates(itinerary, state["overpass_result"])

    # Return data to LangGraph
    return {
        "itinerary": final_itinary,
        "itinerary_html": itinerary_html,
        "chat_id": chat_id,
        "error": False,
        "errorMessage": ""
    }
    
def attach_poi_coordinates(
    itinerary: list[dict],
    overpass_result: list[POI]
) -> list[dict]:

    poi_lookup = {
        poi["name"].strip().lower(): poi
        for poi in overpass_result
    }

    final_itinerary = []

    for item in itinerary:

        poi_name = item["name"].strip().lower()

        poi = poi_lookup.get(poi_name)

        if not poi:
            print(f"POI not found in Overpass: {item['name']}")
            continue

        final_itinerary.append({
            "day": item["day"],
            "block": item["block"],
            "order": item["order"],
            "name": poi["name"],
            "category": poi["type"],
            "description": item["description"],
            "why_visit": item["why_visit"],
            "latitude": float(poi["latitude"]),
            "longitude": float(poi["longitude"])
        })

    return final_itinerary