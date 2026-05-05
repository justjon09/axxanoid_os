import sys
import os

# Ensure import from the root 'memory' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from memory.vector_store import query_memory as vector_store_query
# from memory.database import get_db


def execute_vector_memory_search(query_string: str, where_filter: dict = None) -> str:
    """
    Executes a search against ChromaDB using the query extracted from Q's <tool> tag.
    """
    print(f">>> [TOOL EXECUTING] Searching Memory Vector Vault for: '{query_string}'")
    
    # Query ChromaDB (Fetch top 3 results)
    if where_filter:
        results = vector_store_query(query_text=query_string, n_results=3, where_filter=where_filter)
    else:
        results = vector_store_query(query_text=query_string, n_results=3)
    

    if not results:
        return "[TOOL RESULT: No relevant memories found in the vector vault for this topic.]"
        
    return f"[TOOL RESULT: Memory Context Retrieved]\n{results}"

# def execute_sql_memory_search(query_string: str) -> str:
#     sql_db = get_db()
#     sql_db.