from tools.memory_search.search import execute_vector_memory_search, execute_sql_memory_search
from tools.sqlite_manager.sqlite_manager import execute_sqlite_query

def get_toolbox():
    # These map exactly to the functions passed to the Ollama engine.
    toolbox = {
        'execute_vector_memory_search': execute_vector_memory_search,
        'execute_sql_memory_search': execute_sql_memory_search,
        'execute_sqlite_query': execute_sqlite_query
    }
    return toolbox