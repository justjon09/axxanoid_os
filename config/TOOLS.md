# Tools config 
TODO add explination of each input

Available Tools: [
    {
        Name: Memory Search, 
        Script: memory_search/search.py, 
        Description: "Agent only has immediate access to the last 20 messages. Memory Search allows agent to query local memory."
        Usage:
            "- To search past long-term decisions or concepts, use vector memory: [SEARCH_MEMORY: Vector][Query: <query_string>][Filter: <filter_string>]"
            "- To inspect the internal tables including system_configs, cron_states, current_chats, and agent mainted data, use a RAW SQL query: [SEARCH_MEMORY: SQL][Query: <query_string>]"    
    },
    {
        Name: SQLite Manager
        Script: sqlite_manager/sqlite_manager.py
        Description: "Allows agent to directly execute SQLite queries."
        Usage:
            "- To execute queries: [SQLITE: Query][Query: <query_string]"
    }
    # API manager
    # browser
    # vs code
    # read / write / change permissions
    # image viewer
]