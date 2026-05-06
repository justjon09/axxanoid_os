# Tools config agent explination
TODO add explination of each input

Available Tools: [
    {
        name: SEARCH_MEMORY, 
        script: memory_search/search.py, 
        description: "Agent only has immediate access to the last 20 messages. Memory Search allows agent to query local memory."
        usage:
            "- To search past long-term decisions or concepts, use vector memory: [SEARCH_MEMORY][Type: Vector][Query: <query_string>][Filter: <filter_string>]"
            "- To inspect the internal tables including system_configs, cron_states, current_chats, and agent mainted data, use a RAW SQL query: [SEARCH_MEMORY][Type: SQL][Query: <query_string>]"    
    },
    {
        name: SQLITE
        script: sqlite_manager/sqlite_manager.py
        description: "Allows agent to directly execute SQLite queries."
        usage:
            "- To execute queries: [SQLITE][Query: <query_string]"
    }
    # API manager
    # browser
    # vs code
    # read / write / change permissions
    # image viewer
]