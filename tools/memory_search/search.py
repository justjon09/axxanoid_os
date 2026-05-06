import sys
import os
from sqlalchemy import text

# Ensure import from the root 'memory' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from memory.vector_store import query_memory as vector_store_query
from memory.database import get_db


def execute_vector_memory_search(query_string: str, where_filter: dict = None) -> str:
    """
    Executes a semantic search against ChromaDB for long-term concepts.
    """
    print(f">>> [TOOL EXECUTING] Searching Vector Vault for: '{query_string}' | Filter: {where_filter}")
    # Query ChromaDB (Fetch top 3 results)
    if where_filter:
        results = vector_store_query(query_text=query_string, n_results=3, where_filter=where_filter)
    else:
        results = vector_store_query(query_text=query_string, n_results=3)
    
    if not results:
        return "[TOOL RESULT: No relevant memories found in the vector vault for this topic.]"
    return f"[TOOL RESULT: Memory Context Retrieved]\n{results}"

def execute_sql_memory_search(raw_sql_query: str) -> str:
    """
    Allows agent to execute raw SQL directly against his SQLite database (q_state.db).
    """
    print(f">>> [TOOL EXECUTING] Running Raw SQL: {raw_sql_query}")

    db_generator = get_db()
    db = next(db_generator)

    try:
        # Execute the raw SQL as provided
        result = db.execute(text(raw_sql_query))

        # Run SELECT query and return the row
        if raw_sql_query.strip().lower().startswith("select"):
            rows = result.fetchall()

            if not rows:
                return "[TOOL RESULT: Query executed successfully, but returned 0 rows.]"
            
            # Format the rows cleanly for agent prompt
            output = "[TOOL RESULT: SQL Query Results]\n"
            for row in rows:
                # Convert SQLAlchemy row mapping to dictionary for clean string output
                output += f"{dict(row._mapping)}\n"
            return output
        else:
            return "[TOOL RESULT: Query not of type SELECT, misrouted tool use.]"
        
    except Exception as e:
        return f"[TOOL ERROR: SQL execution failed. Synrax or table erorr: {str(e)}]"
    finally:
        db.close()

# --- SUBPROCESS ENTRY POINT ---
if __name__ == "__main__":
    # sys.argv[0] is the script name. Args start at index 1.
    args = sys.argv[1:]
    
    search_type = None
    query_string = None
    filter_string = None
    
    # Parse the bracket arguments passed by the router
    for arg in args:
        if arg.startswith("Type:"):
            search_type = arg.replace("Type:", "").strip()
        elif arg.startswith("Query:"):
            query_string = arg.replace("Query:", "").strip()
        elif arg.startswith("Filter:"):
            filter_string = arg.replace("Filter:", "").strip()
            
    if not search_type or not query_string:
        print("[TOOL ERROR: Missing Type or Query parameter]")
        sys.exit(1)
        
    if search_type.upper() == "VECTOR":
        where_filter = {"topic": filter_string} if filter_string else None
        print(execute_vector_memory_search(query_string, where_filter))
    elif search_type.upper() == "SQL":
        print(execute_sql_memory_search(query_string))
    else:
        print(f"[TOOL ERROR: Unknown Search Type: {search_type}]")