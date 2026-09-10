import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
import uuid

from graph import travelApp
from history.database_history import save_feedback


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SESSION STATE
# =========================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "error" not in st.session_state:
    st.session_state.error = False

if "errorMessage" not in st.session_state:
    st.session_state.errorMessage = ""

if "itinerary" not in st.session_state:
    st.session_state.itinerary = []

if "itinerary_html" not in st.session_state:
    st.session_state.itinerary_html = ""

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "destination" not in st.session_state:
    st.session_state.destination = ""

if "node_status" not in st.session_state:

    st.session_state.node_status = {
        "user_intent": "pending",
        "nominatim_tool": "pending",
        "overpass_tool": "pending",
        "wikivoyage_rag_node": "pending",
        "itenatanory_tool": "pending",
    }


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ==============================================
       MAIN APPLICATION
       ============================================== */

    .stApp {
        background: #f6f8fb;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }


    /* ==============================================
       HEADER
       ============================================== */

    .app-header {
        text-align: center;
        padding: 10px 0 24px 0;
    }

    .app-title {
        font-size: 34px;
        font-weight: 800;
        color: #101828;
        letter-spacing: -0.5px;
    }

    .app-subtitle {
        font-size: 15px;
        color: #667085;
        margin-top: 5px;
    }


    /* ==============================================
       CARD
       ============================================== */

    .custom-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(16, 24, 40, 0.04);
    }

    .card-title {
        font-size: 18px;
        font-weight: 700;
        color: #101828;
        margin-bottom: 5px;
    }

    .card-description {
        font-size: 13px;
        color: #667085;
        margin-bottom: 14px;
    }


    /* ==============================================
       INPUT
       ============================================== */

    .input-title {
        font-size: 20px;
        font-weight: 700;
        color: #101828;
    }

    .input-subtitle {
        font-size: 13px;
        color: #667085;
        line-height: 1.6;
    }


    /* ==============================================
       AGENT FLOW
       ============================================== */

    .flow-node {
        padding: 10px 12px;
        border-radius: 8px;
        margin: 5px 0;
        font-size: 13px;
        border: 1px solid #e4e7ec;
        background: #f9fafb;
        color: #667085;
    }

    .flow-running {
        background: #eff8ff;
        border-color: #84caff;
        color: #175cd3;
        font-weight: 700;
    }

    .flow-success {
        background: #ecfdf3;
        border-color: #6ce9a6;
        color: #027a48;
        font-weight: 700;
    }

    .flow-error {
        background: #fef3f2;
        border-color: #fda29b;
        color: #b42318;
        font-weight: 700;
    }

    .flow-arrow {
        text-align: center;
        color: #98a2b3;
        font-size: 16px;
        margin: 2px 0;
    }


    /* ==============================================
       TECHNOLOGY
       ============================================== */

    .tech {
        display: inline-block;
        background: #f2f4f7;
        border: 1px solid #e4e7ec;
        border-radius: 20px;
        padding: 5px 10px;
        margin: 3px;
        font-size: 12px;
        color: #344054;
    }


    /* ==============================================
       ERROR
       ============================================== */

    .error-box {
        background: #fff1f0;
        border: 1px solid #fda29b;
        color: #b42318;
        padding: 14px;
        border-radius: 10px;
        margin: 10px 0;
    }


    /* ==============================================
       FEEDBACK
       ============================================== */

    .feedback-selected-up {
        background: #28a745;
        color: white;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
        font-size: 20px;
    }

    .feedback-selected-down {
        background: #dc3545;
        color: white;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
        font-size: 20px;
    }


    /* ==============================================
       SMALL SCREEN
       ============================================== */

    @media (max-width: 900px) {

        .app-title {
            font-size: 28px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.html(
    """
    <div class="app-header">

        <div class="app-title">
            ✈️ AI TRIP PLANNER
        </div>

        <div class="app-subtitle">
            AI-powered personalized travel planning
        </div>

    </div>
    """
)


# =========================================================
# HELPER - NODE STATUS
# =========================================================

def set_node_status(node_name, status):

    if "node_status" not in st.session_state:

        st.session_state.node_status = {}

    st.session_state.node_status[node_name] = status


# =========================================================
# HELPER - FLOW NODE HTML
# =========================================================

def get_flow_node(title, status):

    if status == "running":

        return f"""
        <div class="flow-node flow-running">
            🔵 {title} Running...
        </div>
        """

    elif status == "success":

        return f"""
        <div class="flow-node flow-success">
            ✅ {title}
        </div>
        """

    elif status == "error":

        return f"""
        <div class="flow-node flow-error">
            ❌ {title} Failed
        </div>
        """

    else:

        return f"""
        <div class="flow-node">
            ⏳ {title}
        </div>
        """


# =========================================================
# AGENT FLOW
# =========================================================

def render_agent_flow():

    node_status = st.session_state.node_status

    html = f"""
    <div class="custom-card">

        <div class="card-title">
            🔄 Agent Flow
        </div>

        <div class="card-description">
            Live LangGraph workflow
        </div>

        <div class="flow-node flow-success">
            🚀 START
        </div>

        <div class="flow-arrow">
            ↓
        </div>

        {get_flow_node(
            "User Intent",
            node_status.get("user_intent", "pending")
        )}

        <div class="flow-arrow">
            ↓
        </div>

        {get_flow_node(
            "Nominatim",
            node_status.get("nominatim_tool", "pending")
        )}

        <div class="flow-arrow">
            ↓
        </div>

        {get_flow_node(
            "Overpass",
            node_status.get("overpass_tool", "pending")
        )}

        <div class="flow-arrow">
            ↓
        </div>

        {get_flow_node(
            "Wikivoyage RAG",
            node_status.get("wikivoyage_rag_node", "pending")
        )}

        <div class="flow-arrow">
            ↓
        </div>

        {get_flow_node(
            "Itinerary",
            node_status.get("itenatanory_tool", "pending")
        )}

        <div class="flow-arrow">
            ↓
        </div>

        <div class="flow-node flow-success">
            🏁 END
        </div>

    </div>
    """

    st.html(html)


# =========================================================
# PROJECT ARCHITECTURE
# =========================================================

def render_project_architecture():

    architecture_svg = """
    <svg
        width="100%"
        viewBox="0 0 700 640"
        xmlns="http://www.w3.org/2000/svg"
    >

        <!-- Main Container -->

        <rect
            x="10"
            y="10"
            width="680"
            height="620"
            rx="18"
            fill="#ffffff"
            stroke="#e4e7ec"
        />

        <!-- Title -->

        <text
            x="350"
            y="48"
            text-anchor="middle"
            font-size="22"
            font-weight="bold"
            fill="#101828"
        >
            AI Trip Planner Architecture
        </text>


        <!-- Streamlit -->

        <rect
            x="210"
            y="70"
            width="280"
            height="55"
            rx="10"
            fill="#eff8ff"
            stroke="#84caff"
        />

        <text
            x="350"
            y="104"
            text-anchor="middle"
            font-size="16"
            font-weight="bold"
            fill="#175cd3"
        >
            ✈️ Streamlit UI
        </text>


        <!-- Arrow -->

        <line
            x1="350"
            y1="125"
            x2="350"
            y2="155"
            stroke="#98a2b3"
            stroke-width="2"
        />

        <text
            x="350"
            y="151"
            text-anchor="middle"
            font-size="18"
            fill="#98a2b3"
        >
            ↓
        </text>


        <!-- LangGraph -->

        <rect
            x="190"
            y="160"
            width="320"
            height="60"
            rx="10"
            fill="#ecfdf3"
            stroke="#6ce9a6"
        />

        <text
            x="350"
            y="197"
            text-anchor="middle"
            font-size="17"
            font-weight="bold"
            fill="#027a48"
        >
            🧠 LangGraph Agent
        </text>


        <!-- Arrow -->

        <line
            x1="350"
            y1="220"
            x2="350"
            y2="250"
            stroke="#98a2b3"
            stroke-width="2"
        />


        <!-- OpenAI -->

        <rect
            x="35"
            y="255"
            width="185"
            height="58"
            rx="10"
            fill="#f9fafb"
            stroke="#d0d5dd"
        />

        <text
            x="127"
            y="290"
            text-anchor="middle"
            font-size="15"
            font-weight="bold"
            fill="#344054"
        >
            🤖 OpenAI
        </text>


        <!-- Nominatim -->

        <rect
            x="257"
            y="255"
            width="185"
            height="58"
            rx="10"
            fill="#f9fafb"
            stroke="#d0d5dd"
        />

        <text
            x="350"
            y="290"
            text-anchor="middle"
            font-size="15"
            font-weight="bold"
            fill="#344054"
        >
            📍 Nominatim
        </text>


        <!-- Overpass -->

        <rect
            x="480"
            y="255"
            width="185"
            height="58"
            rx="10"
            fill="#f9fafb"
            stroke="#d0d5dd"
        />

        <text
            x="572"
            y="290"
            text-anchor="middle"
            font-size="15"
            font-weight="bold"
            fill="#344054"
        >
            🗺️ Overpass
        </text>


        <!-- Lines -->

        <line
            x1="127"
            y1="313"
            x2="300"
            y2="355"
            stroke="#98a2b3"
            stroke-width="2"
        />

        <line
            x1="350"
            y1="313"
            x2="350"
            y2="355"
            stroke="#98a2b3"
            stroke-width="2"
        />

        <line
            x1="572"
            y1="313"
            x2="400"
            y2="355"
            stroke="#98a2b3"
            stroke-width="2"
        />


        <!-- Wikivoyage -->

        <rect
            x="190"
            y="360"
            width="320"
            height="60"
            rx="10"
            fill="#fff7ed"
            stroke="#fdba74"
        />

        <text
            x="350"
            y="397"
            text-anchor="middle"
            font-size="16"
            font-weight="bold"
            fill="#c2410c"
        >
            📖 Wikivoyage + RAG
        </text>


        <!-- Arrow -->

        <line
            x1="350"
            y1="420"
            x2="350"
            y2="450"
            stroke="#98a2b3"
            stroke-width="2"
        />


        <!-- Itinerary -->

        <rect
            x="190"
            y="455"
            width="320"
            height="60"
            rx="10"
            fill="#f5f3ff"
            stroke="#c4b5fd"
        />

        <text
            x="350"
            y="492"
            text-anchor="middle"
            font-size="16"
            font-weight="bold"
            fill="#6d28d9"
        >
            🗓️ AI Personalized Itinerary
        </text>


        <!-- Bottom Arrow -->

        <line
            x1="350"
            y1="515"
            x2="350"
            y2="545"
            stroke="#98a2b3"
            stroke-width="2"
        />


        <!-- PostgreSQL -->

        <rect
            x="55"
            y="550"
            width="260"
            height="50"
            rx="10"
            fill="#f9fafb"
            stroke="#d0d5dd"
        />

        <text
            x="185"
            y="581"
            text-anchor="middle"
            font-size="14"
            font-weight="bold"
            fill="#344054"
        >
            💾 PostgreSQL + Feedback
        </text>


        <!-- PyDeck -->

        <rect
            x="385"
            y="550"
            width="260"
            height="50"
            rx="10"
            fill="#f9fafb"
            stroke="#d0d5dd"
        />

        <text
            x="515"
            y="581"
            text-anchor="middle"
            font-size="14"
            font-weight="bold"
            fill="#344054"
        >
            🗺️ PyDeck Interactive Map
        </text>

    </svg>
    """

    st.html(
        f"""
        <div class="custom-card">

            <div class="card-title">
                🏗️ Project Architecture
            </div>

            {architecture_svg}

        </div>
        """
    )


# =========================================================
# TECHNOLOGY STACK
# =========================================================

def render_technology_stack():

    st.html(
        """
        <div class="custom-card">

            <div class="card-title">
                🔌 Technology Stack
            </div>

            <span class="tech">🤖 OpenAI</span>
            <span class="tech">🧠 LangGraph</span>
            <span class="tech">📍 Nominatim</span>
            <span class="tech">🗺️ Overpass</span>
            <span class="tech">📖 Wikivoyage RAG</span>
            <span class="tech">💾 PostgreSQL</span>
            <span class="tech">🗺️ PyDeck</span>

        </div>
        """
    )


# =========================================================
# RESET AGENT FLOW
# =========================================================

def reset_agent_flow():

    st.session_state.node_status = {

        "user_intent": "pending",

        "nominatim_tool": "pending",

        "overpass_tool": "pending",

        "wikivoyage_rag_node": "pending",

        "itenatanory_tool": "pending",

    }


# =========================================================
# RIGHT SIDE PLACEHOLDERS
# =========================================================

left_col, right_col = st.columns(
    [7, 3],
    gap="large"
)


# =========================================================
# RIGHT SIDE
# =========================================================

with right_col:

    flow_placeholder = st.empty()

    technology_placeholder = st.empty()


# =========================================================
# INITIAL RIGHT SIDE
# =========================================================

with flow_placeholder.container():

    render_agent_flow()

with technology_placeholder.container():

    render_technology_stack()


# =========================================================
# LEFT SIDE
# =========================================================

with left_col:

    # -----------------------------------------------------
    # INPUT CARD
    # -----------------------------------------------------

    st.html(
        """
        <div class="custom-card">

            <div class="input-title">
                ✈️ Plan Your Trip
            </div>

            <div class="input-subtitle">
                Tell the AI where you want to travel and
                what kind of trip you want to plan.
            </div>

        </div>
        """
    )


    # -----------------------------------------------------
    # USER INPUT
    # -----------------------------------------------------

    user_query = st.text_area(
        "Travel request",
        placeholder=(
            "Example: Plan 4 days trip for Delhi", "Plan 3 days trip for Kerala"
        ),
        height=120,
        label_visibility="collapsed",
    )


    # -----------------------------------------------------
    # PLAN BUTTON
    # -----------------------------------------------------

    plan_clicked = st.button(
        "✈️ Plan My Trip",
        type="primary",
        width="stretch",
    )


    # =====================================================
    # PLAN TRIP
    # =====================================================

    if plan_clicked:

        # -------------------------------------------------
        # Validate input
        # -------------------------------------------------

        if not user_query.strip():

            st.warning(
                "Please enter your travel request."
            )

        else:

            # ---------------------------------------------
            # Reset state
            # ---------------------------------------------

            st.session_state.error = False

            st.session_state.errorMessage = ""

            st.session_state.itinerary = []

            st.session_state.itinerary_html = ""

            st.session_state.chat_id = None

            st.session_state.feedback = None

            st.session_state.destination = ""

            reset_agent_flow()


            # ---------------------------------------------
            # Initial LangGraph state
            # ---------------------------------------------

            initial_state = {

                "user_query": user_query,

                "session_id":
                    st.session_state.session_id,

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

                "errorMessage": "",

                "final_response": "",

                "itinerary_html": "",
            }


            # ---------------------------------------------
            # Agent execution status
            # ---------------------------------------------

            with st.status(
                "✈️ Planning your trip...",
                expanded=True
            ) as status:

                try:

                    # -------------------------------------
                    # Stream LangGraph
                    # -------------------------------------

                    for event in travelApp.stream(
                        initial_state,
                        stream_mode="updates"
                    ):

                        for node_name, node_data in event.items():

                            # ---------------------------------
                            # USER INTENT
                            # ---------------------------------

                            if node_name == "user_intent":
                                status.update(
                                    label="✈️ Step 1 of 5: Understanding your travel requirements using OpenAI..."
                                )

                            elif node_name == "nominatim_tool":
                                status.update(
                                    label="📍 Step 2 of 5: Identifying your destination using OpenStreetMap Nominatim..."
                                )

                            elif node_name == "overpass_tool":
                                status.update(
                                    label="🗺️ Step 3 of 5: Discovering the best tourist attractions using Overpass API..."
                                )

                            elif node_name == "wikivoyage_rag_node":
                                status.update(
                                    label="📖 Step 4 of 5: Gathering destination information using Wikivoyage and RAG..."
                                )

                            elif node_name == "itenatanory_tool":
                                status.update(
                                    label="🗓️ Step 5 of 5: Creating your personalized itinerary using OpenAI..."
                                )


                            # =================================
                            # ERROR HANDLING
                            # =================================

                            if isinstance(node_data, dict):

                                if node_data.get(
                                    "error",
                                    False
                                ):

                                    st.session_state.error = True

                                    st.session_state.errorMessage = (
                                        node_data.get(
                                            "errorMessage",
                                            "Something went wrong "
                                            "while planning your trip."
                                        )
                                    )


                                    set_node_status(
                                        node_name,
                                        "error"
                                    )


                                    with flow_placeholder.container():
                                        render_agent_flow()


                                    status.update(
                                        label=(
                                            "❌ "
                                            + st.session_state[
                                                "errorMessage"
                                            ]
                                        ),
                                        state="error"
                                    )

                                    break


                                # =================================
                                # MARK NODE SUCCESS
                                # =================================

                                if node_name in [
                                    "user_intent",
                                    "nominatim_tool",
                                    "overpass_tool",
                                    "wikivoyage_rag_node",
                                    "itenatanory_tool",
                                ]:

                                    set_node_status(
                                        node_name,
                                        "success"
                                    )

                                    with flow_placeholder.container():
                                        render_agent_flow()


                                # =================================
                                # SAVE ITINERARY
                                # =================================

                                if "itinerary" in node_data:

                                    st.session_state.itinerary = (
                                        node_data["itinerary"]
                                    )


                                # =================================
                                # SAVE HTML ITINERARY
                                # =================================

                                if "itinerary_html" in node_data:

                                    st.session_state.itinerary_html = (
                                        node_data[
                                            "itinerary_html"
                                        ]
                                    )


                                # =================================
                                # SAVE DESTINATION
                                # =================================

                                if "destination" in node_data:

                                    st.session_state.destination = (
                                        node_data["destination"]
                                    )


                                # =================================
                                # SAVE CHAT ID
                                # =================================

                                if "chat_id" in node_data:

                                    st.session_state.chat_id = (
                                        node_data["chat_id"]
                                    )


                                # =================================
                                # SAVE ERROR
                                # =================================

                                if "error" in node_data:

                                    st.session_state.error = (
                                        node_data["error"]
                                    )

                                if "errorMessage" in node_data:

                                    st.session_state.errorMessage = (
                                        node_data[
                                            "errorMessage"
                                        ]
                                    )


                    # -----------------------------------------
                    # Final status
                    # -----------------------------------------

                    if not st.session_state.error:

                        status.update(
                            label="✅ Your itinerary is ready!",
                            state="complete"
                        )

                except Exception as e:

                    st.session_state.error = True

                    st.session_state.errorMessage = (
                        f"Unexpected error: {str(e)}"
                    )

                    status.update(
                        label=(
                            "❌ "
                            + st.session_state.errorMessage
                        ),
                        state="error"
                    )


                    # Mark currently running nodes as error

                    for node_name, node_state in (
                        st.session_state.node_status.items()
                    ):

                        if node_state == "running":

                            st.session_state.node_status[
                                node_name
                            ] = "error"


                    with flow_placeholder.container():
                        render_agent_flow()


# =========================================================
# ERROR DISPLAY
# =========================================================

if (
    st.session_state.get("error", False)
):

    with left_col:

        st.html(
            f"""
            <div class="error-box">

                ⚠️
                <b>Unable to create your itinerary</b>

                <br><br>

                {st.session_state.get(
                    "errorMessage",
                    "Something went wrong."
                )}

            </div>
            """
        )


# =========================================================
# ITINERARY
# =========================================================

if (
    st.session_state.get("itinerary")
    and not st.session_state.get("error", False)
):

    with left_col:

        # -------------------------------------------------
        # ITINERARY HEADER
        # -------------------------------------------------

        itinerary_col, up_col, down_col = st.columns(
            [8, 0.7, 0.7]
        )


        with itinerary_col:

            st.subheader(
                "🗓️ Your Itinerary"
            )


        # -------------------------------------------------
        # FEEDBACK - UP
        # -------------------------------------------------

        with up_col:

            if st.session_state.feedback == "up":

                st.markdown(
                    """
                    <div class="feedback-selected-up">
                        👍
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                if st.button(
                    "👍",
                    key=(
                        f"up_"
                        f"{st.session_state.chat_id}"
                    ),
                    width="stretch",
                ):

                    if st.session_state.chat_id:

                        save_feedback(
                            chat_id=(
                                st.session_state.chat_id
                            ),
                            session_id=(
                                st.session_state.session_id
                            ),
                            feedback="up"
                        )

                        st.session_state.feedback = "up"

                        st.rerun()


        # -------------------------------------------------
        # FEEDBACK - DOWN
        # -------------------------------------------------

        with down_col:

            if st.session_state.feedback == "down":

                st.markdown(
                    """
                    <div class="feedback-selected-down">
                        👎
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                if st.button(
                    "👎",
                    key=(
                        f"down_"
                        f"{st.session_state.chat_id}"
                    ),
                    width="stretch",
                ):

                    if st.session_state.chat_id:

                        save_feedback(
                            chat_id=(
                                st.session_state.chat_id
                            ),
                            session_id=(
                                st.session_state.session_id
                            ),
                            feedback="down"
                        )

                        st.session_state.feedback = "down"

                        st.rerun()


        # =================================================
        # ITINERARY HTML
        # =================================================

        if st.session_state.get(
            "itinerary_html"
        ):

            st.html(
                st.session_state[
                    "itinerary_html"
                ]
            )


        # =================================================
        # MAP
        # =================================================

        st.subheader(
            "🗺️ Interactive Trip Map"
        )


        itinerary = st.session_state.itinerary


        # -------------------------------------------------
        # Convert itinerary to DataFrame
        # -------------------------------------------------

        try:

            df = pd.DataFrame(
                itinerary
            )

        except Exception as e:

            st.error(
                f"Unable to create map data: {e}"
            )

            df = pd.DataFrame()


        # -------------------------------------------------
        # Validate required columns
        # -------------------------------------------------

        required_columns = [
            "day",
            "latitude",
            "longitude",
        ]


        if not df.empty and all(
            column in df.columns
            for column in required_columns
        ):

            # ---------------------------------------------
            # Day selector
            # ---------------------------------------------

            days = sorted(
                df["day"]
                .dropna()
                .unique()
            )


            selected_day = st.selectbox(
                "Select Day",
                ["All Days"]
                + [
                    f"Day {int(day)}"
                    for day in days
                ],
                key="selected_map_day",
            )


            # ---------------------------------------------
            # Filter data
            # ---------------------------------------------

            if selected_day == "All Days":

                map_df = df.copy()

            else:

                day_number = int(
                    selected_day.split(" ")[1]
                )

                map_df = df[
                    df["day"] == day_number
                ].copy()


            # ---------------------------------------------
            # Convert coordinates
            # ---------------------------------------------

            map_df["latitude"] = pd.to_numeric(
                map_df["latitude"],
                errors="coerce"
            )

            map_df["longitude"] = pd.to_numeric(
                map_df["longitude"],
                errors="coerce"
            )


            map_df = map_df.dropna(
                subset=[
                    "latitude",
                    "longitude"
                ]
            )


            # =================================================
            # MAP
            # =================================================

            if not map_df.empty:

                # ---------------------------------------------
                # SVG PIN
                # ---------------------------------------------

                pin_svg = """
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="40"
                    height="50"
                    viewBox="0 0 40 50"
                >

                    <path
                        d="
                        M20 0
                        C9 0 0 9 0 20
                        C0 35 20 50 20 50
                        C20 50 40 35 40 20
                        C40 9 31 0 20 0
                        Z
                        "
                        fill="#e53935"
                    />

                    <circle
                        cx="20"
                        cy="20"
                        r="8"
                        fill="white"
                    />

                </svg>
                """


                # ---------------------------------------------
                # Base64 SVG
                # ---------------------------------------------

                pin_base64 = base64.b64encode(
                    pin_svg.encode()
                ).decode()


                pin_url = (
                    "data:image/svg+xml;base64,"
                    + pin_base64
                )


                # ---------------------------------------------
                # Icon Data
                # ---------------------------------------------

                map_df["icon_data"] = [

                    {
                        "url": pin_url,
                        "width": 40,
                        "height": 50,
                        "anchorY": 50,
                    }

                    for _ in range(
                        len(map_df)
                    )
                ]


                # ---------------------------------------------
                # Icon Layer
                # ---------------------------------------------

                pin_layer = pdk.Layer(

                    "IconLayer",

                    data=map_df,

                    get_icon="icon_data",

                    get_position=(
                        "[longitude, latitude]"
                    ),

                    get_size=40,

                    size_scale=1,

                    pickable=True,

                    icon_billboard=True,
                )


                # ---------------------------------------------
                # Map Center
                # ---------------------------------------------

                center_latitude = (
                    map_df["latitude"].mean()
                )

                center_longitude = (
                    map_df["longitude"].mean()
                )


                # ---------------------------------------------
                # View State
                # ---------------------------------------------

                view_state = pdk.ViewState(

                    latitude=center_latitude,

                    longitude=center_longitude,

                    zoom=11,
                )


                # ---------------------------------------------
                # Tooltip
                # ---------------------------------------------

                tooltip = {

                    "html": """
                    <b>{name}</b><br/>
                    Category: {category}<br/>
                    Day: {day}<br/>
                    Time: {block}<br/>
                    Order: {order}
                    """,

                    "style": {
                        "backgroundColor": "white",
                        "color": "black",
                    }
                }


                # ---------------------------------------------
                # PyDeck
                # ---------------------------------------------

                deck = pdk.Deck(

                    layers=[
                        pin_layer
                    ],

                    initial_view_state=view_state,

                    tooltip=tooltip,
                )


                # ---------------------------------------------
                # Render map
                # ---------------------------------------------

                st.pydeck_chart(
                    deck,
                    width="stretch"
                )


            else:

                st.info(
                    "No valid coordinates found "
                    "for this day."
                )


        else:

            st.info(
                "Map data is not available in "
                "the generated itinerary."
            )