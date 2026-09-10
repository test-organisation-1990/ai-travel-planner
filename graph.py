from Nodes.user_intent import user_intent
from Nodes.nominatim_over_tool import nominatim_over_tool
from Nodes.overpass_tool import overpass_tool
from Nodes.wikivoyage_rag_node import wikivoyage_rag_node
from Nodes.itenatanory_tool import itenatanory_tool
from Nodes.validate_errors import validate_errors
from Common.state import TravelState
from langgraph.graph import StateGraph, START, END

graph = StateGraph(TravelState)

graph.add_node("user_intent", user_intent)
graph.add_node("nominatim_tool", nominatim_over_tool)
graph.add_node("overpass_tool", overpass_tool)
graph.add_node("itenatanory_tool", itenatanory_tool)
graph.add_node("wikivoyage_rag_node", wikivoyage_rag_node)

graph.add_edge(START, "user_intent")

graph.add_conditional_edges(
    "user_intent",
    validate_errors,
    {
        "success": "nominatim_tool",
        "error": END
    }
)

graph.add_conditional_edges(
    "nominatim_tool",
    validate_errors,
    {
        "success": "overpass_tool",
        "error": END
    }
)

graph.add_conditional_edges(
    "overpass_tool",
    validate_errors,
    {
        "success": "wikivoyage_rag_node",
        "error": END
    }
)

graph.add_conditional_edges(
    "wikivoyage_rag_node",
    validate_errors,
    {
        "success": "itenatanory_tool",
        "error": END
    }
)

graph.add_edge("itenatanory_tool", END)

""" graph.add_edge(START, "user_intent")
graph.add_edge("user_intent", "nominatim_tool")
graph.add_edge("nominatim_tool", "overpass_tool")
graph.add_edge("overpass_tool", "wikivoyage_rag_node")
graph.add_edge("wikivoyage_rag_node", "itenatanory_tool")
graph.add_edge("itenatanory_tool", END) """
travelApp = graph.compile()