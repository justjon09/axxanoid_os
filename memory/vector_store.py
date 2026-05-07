import os
os.environ["ANONYMIZED_TELEMETRY"] = "False" # Nuke telemetry before Chroma even loads
os.environ["CHROMA_TELEMETRY_IMPL"] = "none" # This completely disables the buggy Posthog capture
import chromadb
from chromadb.config import Settings

# Define where the vector DB lives
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, 'chroma_data')

# Initialize the presestent client (saves to disk not RAM) and strictly disable telemetry (no phoning home)
client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False)
)

# Create a specific collection for Q's project knowledge
collection = client.get_or_create_collection(name="q_workspace_memory")

def add_to_memory(doc_id: str, content: str, metadata: dict = None):
    """
    Injects a document, code snippet, or rule into Q's vector memory.
    """
    if metadata:
        collection.upsert(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
    else:
        # If no metadata is provided, do not pass the metadatas parameter at all
        collection.upsert(
            documents=[content],
            ids=[doc_id]
        )
    print(f">>> [MEMORY] Ingested '{doc_id}' into ChromaDB.")

def query_memory(query_text: str, n_results: int = 2, where_filter: dict = None) -> str:
    """
    Searches the vector store for context relevent to the users prompt.
    Returns a formatted string ready to be injected into Q's prompt.
    Can be filtered by metadata (e.g. where_filter={"category": "legal"}).
    """
    # If the database is empty dont try to query it
    if collection.count() == 0:
        return ""

    # Adjust n_results if the database has fewer documents then requested
    results_to_fetch = min(n_results, collection.count())

    # Build the query arguments dynamically
    query_kwargs = {
        "query_texts": [query_text],
        "n_results": results_to_fetch
    }
    
    # If a metadata filter is provided, apply it to the ChromaDB query
    if where_filter:
        query_kwargs["where"] = where_filter

    # Execute the search
    results = collection.query(**query_kwargs)
    
    context = ""
    if results['documents'] and results['documents'][0]:
        context = "--- LOCAL WORKSPACE CONTEXT ---\n"
        for idx, doc in enumerate(results['documents'][0]):
            doc_id = results['ids'][0][idx]
            # We can also expose the metadata to Q so he knows what kind of file he is reading
            meta = results['metadatas'][0][idx]
            context += f"[Source: {doc_id} | Tags: {meta}]: {doc}\n\n"
        context += "-------------------------------\n"
    
    return context

def get_memory_topics():
    """
    Queries ChromaDB for all stored memories and extracts unique document IDs so the UI can display what agent remembers.
    """
    try:
        # Fetch all
        results = collection.get()
        
        if not results or not results["ids"]:
            return []
        # Extract the unique Document IDs
        topics = set(results["ids"])               
        return sorted(list(topics))
    except Exception as e:
        print(f"Error fetching memory topics: {e}")
        return []