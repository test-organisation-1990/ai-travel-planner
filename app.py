import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
import uuid
from graph import travelApp

if "session_id" not in st.session_state:
    session_id = st.session_state.session_id = str(uuid.uuid4())

st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI Trip Planner")

st.write("Plan your trip using AI, OpenStreetMap and Wikivoyage.")


# ---------------------------------------------------------
# User Input
# ---------------------------------------------------------
user_query = st.text_area(
    "Where would you like to travel?",
    placeholder="Example: Plan 4 days trip for Japan",
    height=100
)
st.session_state["error"] = False

if st.button("Plan My Trip", type="primary"):

    if not user_query.strip():
        st.warning("Please enter your travel request.")

    else:
        st.session_state["error"] = False
        st.session_state["errorMessage"] = ""
        st.session_state["itinerary"] = []
        st.session_state["itinerary_html"] = ""
        st.session_state["chat_id"] = None
        
        initial_state = {
            "user_query": user_query,
            "session_id": st.session_state.session_id,
            "destination": "",
            "source": "",
            "chat_id": "",
            "minimum_budget": None,
            "maximum_budget": None,
            "destination_latitude": 0.0,
            "destination_longitude": 0.0,
            "destination_display_name": "",
            "overpass_result": [],
            "wikivoyage_result": "",
            "itinerary": [],
            "error": False,
            "errorMessage": False,
            "final_response": "",
            "itinerary_html": ""
        }
        
        with st.status(
            "✈️ Planning your trip...",
            expanded=False
        ) as status:

            for event in travelApp.stream(
                initial_state,
                stream_mode="updates"
            ):

                for node_name, node_data in event.items():

                    # -----------------------------------------
                    # Show current node progress
                    # -----------------------------------------

                    if node_name == "user_intent":

                        status.update(
                            label="✈️ Understanding your travel requirements..."
                        )

                    elif node_name == "nominatim__tool":

                        status.update(
                            label="📍 Identifying your destination..."
                        )

                    elif node_name == "overpass_tool":

                        status.update(
                            label="🗺️ Exploring the best tourist places..."
                        )

                    elif node_name == "wikivoyage_rag_node":

                        status.update(
                            label="📖 Gathering useful travel information..."
                        )

                    elif node_name == "itenatanory_tool":

                        status.update(
                            label="🗓️ Preparing your personalized itinerary..."
                        )

                    # -----------------------------------------
                    # Handle errors from any node
                    # -----------------------------------------

                    if node_data.get("error", False):

                        st.session_state["error"] = True

                        st.session_state["errorMessage"] = node_data.get(
                            "errorMessage",
                            "Something went wrong while planning your trip."
                        )

                        status.update(
                            label=f"❌ {st.session_state['errorMessage']}",
                            state="error"
                        )

                        # Stop processing this event
                        break

                    # -----------------------------------------
                    # Save itinerary
                    # -----------------------------------------

                    if "itinerary" in node_data:

                        st.session_state["itinerary"] = (
                            node_data["itinerary"]
                        )

                    # -----------------------------------------
                    # Save HTML itinerary
                    # -----------------------------------------

                    if "itinerary_html" in node_data:

                        st.session_state["itinerary_html"] = (
                            node_data["itinerary_html"]
                        )

                    # -----------------------------------------
                    # Save destination
                    # -----------------------------------------

                    if "destination" in node_data:

                        st.session_state["destination"] = (
                            node_data["destination"]
                        )

                    # -----------------------------------------
                    # Save chat ID
                    # -----------------------------------------

                    if "chat_id" in node_data:

                        st.session_state["chat_id"] = (
                            node_data["chat_id"]
                        )

                    # -----------------------------------------
                    # Save error values if returned
                    # -----------------------------------------

                    if "error" in node_data:

                        st.session_state["error"] = (
                            node_data["error"]
                        )

                    if "errorMessage" in node_data:

                        st.session_state["errorMessage"] = (
                            node_data["errorMessage"]
                        )


            # ---------------------------------------------
            # Final status
            # ---------------------------------------------

            if not st.session_state.get("error", False):

                status.update(
                    label="✅ Your itinerary is ready!",
                    state="complete"
                )
            
        st.session_state.feedback = None


# ---------------------------------------------------------
# Display Itinerary
# ---------------------------------------------------------
if "error" in st.session_state and st.session_state["error"]:
    st.subheader("🗓️ Your Itinerary")
    st.markdown(
    f"""
    <div style="
        background-color: #ffe6e6;
        color: #cc0000;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #ff9999;
        margin: 10px 0;
    ">
        ⚠️ {st.session_state["errorMessage"]}
    </div>
    """,
    unsafe_allow_html=True
)
    
if (
    "itinerary" in st.session_state
    and not st.session_state.get("error", False)
):

    itinerary = st.session_state["itinerary"]

    col1, col2, col3 = st.columns([7, 0.5,0.5])
    chat_id = st.session_state["chat_id"]
    with col1:
        st.subheader("🗓️ Your Itinerary")
    with col2:      
        if st.session_state.feedback == "up":

            st.markdown(
                """
                <div style="
                    background-color:#28a745;
                    color:white;
                    padding:8px;
                    border-radius:8px;
                    text-align:center;
                    font-size:20px;
                ">
                    👍
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            if st.button("👍", key=f"up_{chat_id}"):
                """ save_feedback(
                    chat_id=chat_id,
                    session_id=st.session_state.session_id,
                    feedback="up"
                ) """
                st.session_state.feedback = "up"
                st.rerun()
    with col3:
            
        if st.session_state.feedback == "down":

            st.markdown(
                """
                <div style="
                    background-color:#dc3545;
                    color:white;
                    padding:8px;
                    border-radius:8px;
                    text-align:center;
                    font-size:20px;
                ">
                    👎
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            if st.button("👎", key=f"down_{chat_id}"):
                """ save_feedback(
                    chat_id=chat_id,
                    session_id=st.session_state.session_id,
                    feedback="down"
                ) """
                st.session_state.feedback = "down"
                st.rerun()
        

    df = pd.DataFrame(itinerary)
    
    st.markdown(
        st.session_state["itinerary_html"],
        unsafe_allow_html=True
    )
    
    st.subheader("🗺️ Trip Map")


    days = sorted(df["day"].unique())

    selected_day = st.selectbox(
        "Select Day",
        ["All Days"] + [f"Day {day}" for day in days]
    )


    if selected_day == "All Days":

        map_df = df.copy()

    else:

        day_number = int(selected_day.split(" ")[1])

        map_df = df[
            df["day"] == day_number
        ].copy()


    # ---------------------------------------------------------
    # Convert coordinates to numbers
    # ---------------------------------------------------------

    map_df["latitude"] = pd.to_numeric(
        map_df["latitude"],
        errors="coerce"
    )

    map_df["longitude"] = pd.to_numeric(
        map_df["longitude"],
        errors="coerce"
    )


    map_df = map_df.dropna(
        subset=["latitude", "longitude"]
    )


    if not map_df.empty:

        # -----------------------------------------------------
        # Create normal map pin
        # -----------------------------------------------------

        pin_svg = """
        <svg xmlns="http://www.w3.org/2000/svg"
            width="40"
            height="50"
            viewBox="0 0 40 50">

            <path
                d="M20 0C9 0 0 9 0 20
                c0 15 20 30 20 30
                s20-15 20-30C40 9 31 0 20 0z"
                fill="#e53935"/>

            <circle
                cx="20"
                cy="20"
                r="8"
                fill="white"/>

        </svg>
        """

        pin_base64 = base64.b64encode(
            pin_svg.encode()
        ).decode()

        pin_url = (
            f"data:image/svg+xml;base64,{pin_base64}"
        )


        # Add icon information
        map_df["icon_data"] = [
            {
                "url": pin_url,
                "width": 40,
                "height": 50,
                "anchorY": 50,
            }
            for _ in range(len(map_df))
        ]


        # -----------------------------------------------------
        # Pin Layer
        # -----------------------------------------------------

        pin_layer = pdk.Layer(
            "IconLayer",

            data=map_df,

            get_icon="icon_data",

            get_position="[longitude, latitude]",

            get_size=40,

            size_scale=1,

            pickable=True,

            icon_billboard=True,
        )


        # -----------------------------------------------------
        # Map Center
        # -----------------------------------------------------

        center_latitude = map_df["latitude"].mean()

        center_longitude = map_df["longitude"].mean()


        view_state = pdk.ViewState(
            latitude=center_latitude,
            longitude=center_longitude,
            zoom=11,
        )


        # -----------------------------------------------------
        # Tooltip
        # -----------------------------------------------------

        tooltip = {
            "html": """
            <b>{name}</b><br/>
            Category: {category}<br/>
            Day: {day}<br/>
            Time: {block}<br/>
            Order: {order}
            """
        }


        # -----------------------------------------------------
        # Map
        # -----------------------------------------------------

        deck = pdk.Deck(
            layers=[
                pin_layer
            ],

            initial_view_state=view_state,

            tooltip=tooltip,
        )


        st.pydeck_chart(
            deck,
            width="stretch"
        )