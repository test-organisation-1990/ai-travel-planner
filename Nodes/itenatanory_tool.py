from Common.state import TravelState, POI
from Common.Model import llm
from history.database_history import save_chat

import json


def itenatanory_tool(state: TravelState):

    prompt = f"""
You are an expert AI travel planner.

Your task is to create a practical, realistic, and user-friendly travel itinerary
using ONLY the data provided in this prompt.

========================
USER TRAVEL REQUEST
========================

{state["user_query"]}

========================
EXTRACTED TRAVEL DETAILS
========================

Destination:
{state["destination"]}

Source:
{state["source"]}

Minimum Budget:
{state.get("minimum_budget", "")}

Maximum Budget:
{state.get("maximum_budget", "")}

========================
OPENSTREETMAP TOURIST PLACES
========================

The following places were retrieved from OpenStreetMap/Overpass.

IMPORTANT:
- These are the ONLY places that you are allowed to include in the itinerary.
- You MUST NOT invent, assume, or add any tourist place that is not present in this list.
- Use the exact POI name provided by OpenStreetMap.

{state["overpass_result"]}

========================
WIKIVOYAGE INFORMATION
========================

Use this information only when it is available.

{state["wikivoyage_result"]}

==================================================
ITINERARY PLANNING INSTRUCTIONS
==================================================

1. Determine the number of travel days from the user's request.

2. If the user explicitly provides a number of days, use that number.

3. If the user does not provide a number of days, create a maximum of 5 days.

4. Do NOT create more days than the user requested.

5. Select ONLY the best and most relevant tourist places from the
   OpenStreetMap POI list.

6. Do NOT invent tourist attractions, restaurants, hotels, activities,
   transportation, historical facts, prices, opening hours, distances,
   travel times, or other information that is not present in the supplied data.

7. If the OpenStreetMap data contains many POIs, DO NOT include every POI.
   Select the most useful and relevant places for a normal tourist.

8. Prefer POIs that:
   - are clearly tourist attractions,
   - are relevant to the destination,
   - provide variety,
   - can reasonably be visited together,
   - and have useful supporting information in Wikivoyage when available.

9. Avoid repeating the same POI.

10. Each POI must appear only once in the itinerary unless the supplied
    data explicitly indicates that multiple visits are appropriate.

11. Arrange POIs in a sensible order within each day.

12. Try to distribute the selected POIs across the available days instead of
    putting most attractions into a single day.

13. Do not overload a single day with too many places.

14. If there are not enough valid POIs for all requested days, use only the
    available valid POIs. Do NOT invent additional places to fill the days.

15. If there are more POIs than can reasonably fit into the requested number
    of days, select only the strongest/relevant POIs.

16. For every itinerary item, use exactly one of these blocks:

    "Morning"
    "Afternoon"
    "Evening"

17. The order number must restart from 1 for every day.

Example:

Day 1:
Morning -> order 1
Afternoon -> order 2
Evening -> order 3

Day 2:
Morning -> order 1
Afternoon -> order 2
Evening -> order 3

18. Do not create a block other than Morning, Afternoon, or Evening.

==================================================
DESCRIPTION AND WHY_VISIT
==================================================

For every selected POI:

"description":
- Write a short, useful description of the place.
- Use information from the supplied OpenStreetMap and Wikivoyage data.
- Keep the language simple and natural.
- Do not add unsupported facts.
- Do not mention latitude or longitude.

"why_visit":
- Explain why this particular place is worth visiting.
- Base the explanation ONLY on the supplied information.
- Do not make generic claims that are not supported by the data.
- Do not invent experiences, historical facts, activities, popularity,
  ratings, or special features.

If Wikivoyage does not contain useful information for a POI, use only
the information available in the OpenStreetMap data.

==================================================
IMPORTANT DATA ACCURACY RULE
==================================================

The OpenStreetMap POI list is the source of truth for PLACE NAMES.

Before generating the final response:

1. Check every "name" against the OpenStreetMap POI list.
2. Make sure the name exists exactly in the provided POI data.
3. Do not modify the POI name.
4. Do not add a place based only on your own knowledge.
5. Do not add a place mentioned in Wikivoyage if that place is not also
   present in the OpenStreetMap POI list.

==================================================
HTML GENERATION
==================================================

Generate an HTML representation of EXACTLY the same itinerary contained
in the "itinerary" JSON array.

The HTML MUST:

- Contain exactly the same days.
- Contain exactly the same POIs.
- Use exactly the same POI names.
- Use exactly the same descriptions.
- Use exactly the same why_visit information.
- Never add an additional place.
- Never remove a place.
- Never generate latitude or longitude.

HTML requirements:

- Start with <div>
- Do NOT use <html>, <head>, or <body>
- Create one section for each day.
- Display the day using <h2>.
- Group places using Morning, Afternoon, and Evening.
- Display each place prominently using <h3> or <h4>.
- Display the description using <p>.
- Display why the place is worth visiting using <p>.
- Use only safe HTML elements:

  div
  h2
  h3
  h4
  p
  ul
  li
  strong
  span

- Do NOT use JavaScript.
- Do NOT use:
  <script>
  <iframe>
  onclick
  onload
  or any other event handler.

- Do NOT use Markdown inside the HTML.
- Keep the HTML simple and readable.

==================================================
FINAL VALIDATION
==================================================

Before returning the answer, perform these checks:

CHECK 1:
Every itinerary POI exists in the OpenStreetMap POI list.

CHECK 2:
Every POI name exactly matches the OpenStreetMap name.

CHECK 3:
No POI is invented.

CHECK 4:
The number of days matches the user's requested number of days,
unless the user did not specify a duration, in which case use at most 5 days.

CHECK 5:
Every itinerary item has:
- day
- block
- order
- name
- description
- why_visit

CHECK 6:
The block is only:
Morning, Afternoon, or Evening.

CHECK 7:
Order starts at 1 for every day.

CHECK 8:
HTML contains exactly the same POIs as the JSON itinerary.

CHECK 9:
HTML descriptions and why_visit values match the JSON itinerary.

CHECK 10:
No latitude or longitude is included.

CHECK 11:
Return syntactically valid JSON.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Do NOT use Markdown.

Do NOT wrap the JSON in ```json.

Do NOT provide explanations before or after the JSON.

Use EXACTLY this structure:

{{
    "itinerary": [
        {{
            "day": 1,
            "block": "Morning",
            "order": 1,
            "name": "Exact POI name from OpenStreetMap",
            "description": "Short description based only on supplied data.",
            "why_visit": "Reason to visit based only on supplied data."
        }},
        {{
            "day": 1,
            "block": "Afternoon",
            "order": 2,
            "name": "Exact POI name from OpenStreetMap",
            "description": "Short description based only on supplied data.",
            "why_visit": "Reason to visit based only on supplied data."
        }}
    ],
    "html": "<div class='itinerary'>...</div>"
}}

Remember:

- JSON is the primary output.
- HTML must represent the same itinerary.
- OpenStreetMap POIs are the only allowed places.
- Never invent places or facts.
- Exact POI names must be preserved.
- Return ONLY valid JSON.
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