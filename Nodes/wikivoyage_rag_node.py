from Common.state import TravelState
from services.wikivoyage import create_vector_store, retrieve_wikivoyage, index_wikivoyage, format_documents

def wikivoyage_rag_node(state: TravelState):

    destination = state.get(
        "destination"
    )

    user_query = state.get(
        "user_query"
    )

    print(
        f"\nSearching Wikivoyage RAG for: {destination}"
    )

    # -----------------------------------------------------
    # First check whether data exists in Chroma.
    # -----------------------------------------------------

    vector_store = create_vector_store()

    # -----------------------------------------------------
    # Fetch + index destination if required
    # -----------------------------------------------------

    try:

        documents = retrieve_wikivoyage(
            destination,
            user_query,
            k=5
        )

    except Exception:

        print(
            "No indexed Wikivoyage data found."
        )

    vector_store = index_wikivoyage(
        destination
    )

    if vector_store is None:

        return {
            "wikivoyage_result":
                "No Wikivoyage information available."
        }

    documents = retrieve_wikivoyage(
        destination,
        user_query,
        k=5
    )

    # -----------------------------------------------------
    # Format retrieved documents
    # -----------------------------------------------------

    context = format_documents(
        documents
    )

    return {
        "wikivoyage_result": context
    }