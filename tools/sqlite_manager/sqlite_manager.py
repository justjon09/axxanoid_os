import sys
import os
from sqlalchemy import text

# Ensure import from the root 'memory' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from memory.database import get_db

def execute_sqlite_query(raw_sql_query: str) -> str:
    """
    Allows Agent to execute raw SQL directly against SQLite database (q_state.db).
    """
    print(f">>> [TOOL EXECUTING] Running Raw SQL: {raw_sql_query}")
    
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # Execute the raw SQL Q provided
        result = db.execute(text(raw_sql_query))
        
        # If it's a modifying query (like an UPDATE), commit it
        if raw_sql_query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            db.commit()
            return f"[TOOL RESULT: SQL executed successfully. {result.rowcount} rows affected.]"
            
        # If it's a SELECT query, return the rows
        rows = result.fetchall()
        if not rows:
            return "[TOOL RESULT: Query executed successfully, but returned 0 rows.]"
            
        # Format the rows cleanly for Q's prompt
        output = "[TOOL RESULT: SQL Query Results]\n"
        for row in rows:
            # Convert SQLAlchemy row mapping to a dictionary for clean string output
            output += f"{dict(row._mapping)}\n"
            
        return output
        
    except Exception as e:
        return f"[TOOL ERROR: SQL execution failed. Syntax or table error: {str(e)}]"
    finally:
        db.close()

# --- SUBPROCESS ENTRY POINT ---
if __name__ == "__main__":
    args = sys.argv[1:]
    query_string = None
    
    for arg in args:
        if arg.startswith("Query:"):
            query_string = arg.replace("Query:", "").strip()
            
    if not query_string:
        print("[TOOL ERROR: Missing Query parameter]")
        sys.exit(1)
        
    print(execute_sqlite_query(query_string))
    sys.exit(0)