import requests
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import streamlit as st

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

WIKIVOYAGE_API_URL = st.secrets["WIKIVOYAGE_API_URL"]
CHROMA_DIRECTORY = st.secrets["CHROMA_DIRECTORY"]
COLLECTION_NAME = st.secrets["COLLECTION_NAME"]


# ---------------------------------------------------------
# 1. Fetch Wikivoyage article
# ---------------------------------------------------------

def fetch_wikivoyage(destination: str) -> str:
    """
    Fetch travel information from English Wikivoyage.
    """

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": destination,
        "redirects": 1,
        "formatversion": 2
    }
    
    headers = {
        "User-Agent": "trip-planner-ai/1.0"
    }

    try:

        response = requests.get(
            WIKIVOYAGE_API_URL,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        pages = data.get("query", {}).get("pages", [])

        if not pages:
            return ""

        page = pages[0]

        # Page does not exist
        if "missing" in page:
            return ""

        content = page.get("extract", "")

        return content

    except requests.RequestException as e:

        print(f"Wikivoyage API error: {e}")

        return ""

    except Exception as e:

        print(f"Unexpected Wikivoyage error: {e}")

        return ""


# ---------------------------------------------------------
# 2. Split Wikivoyage article into chunks
# ---------------------------------------------------------

def split_documents(
    text: str,
    destination: str
):
    """
    Split Wikivoyage article into smaller chunks.
    """

    if not text:
        return []

    document = Document(
        page_content=text,
        metadata={
            "source": "Wikivoyage",
            "destination": destination
        }
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    documents = text_splitter.split_documents(
        [document]
    )

    return documents


# ---------------------------------------------------------
# 3. Create / load Chroma
# ---------------------------------------------------------

def create_vector_store():

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIRECTORY
    )

    return vector_store


# ---------------------------------------------------------
# 4. Index Wikivoyage document
# ---------------------------------------------------------

def index_wikivoyage(
    destination: str
):
    """
    Fetch Wikivoyage article,
    split it,
    generate embeddings,
    and save into Chroma.
    """

    content = fetch_wikivoyage(destination)

    if not content:

        print(
            f"No Wikivoyage information found for {destination}"
        )

        return None

    print(
        f"Downloaded {len(content)} characters"
    )

    documents = split_documents(
        content,
        destination
    )

    vector_store = create_vector_store()

    # Add documents to Chroma
    vector_store.add_documents(
        documents
    )

    return vector_store


# ---------------------------------------------------------
# 5. Retrieve relevant Wikivoyage information
# ---------------------------------------------------------

def retrieve_wikivoyage(
    destination: str,
    user_query: str,
    k: int = 5
):
    """
    Retrieve the most relevant Wikivoyage chunks.
    """

    vector_store = create_vector_store()

    search_query = f"""
    Destination: {destination}

    Travel requirement:
    {user_query}
    """

    documents = vector_store.similarity_search(
        search_query,
        k=k
    )

    return documents


# ---------------------------------------------------------
# 6. Convert retrieved documents to text
# ---------------------------------------------------------

def format_documents(
    documents
) -> str:

    if not documents:
        return "No Wikivoyage information found."

    result = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        result.append(
            f"""
--- Wikivoyage Source {index} ---

{document.page_content}
"""
        )

    return "\n".join(result)
