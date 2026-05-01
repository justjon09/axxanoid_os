# Heartbeat config 
TODO add explination of each input

Heartbeat Prompt List Items: [
    "Did the human leave any tasks unfinished? ",
    "Based on the $1k per week income floor, is the human currently distracted by 'Wood Gathering'? ",
    "Do you need to execute any background memory organization? "
]

Run audits: [
    {script: hardware.py, name: HARDWARE_AUDIT, description: "compare actuall availbe hardware to known hardware configuration"},
    # MEMORY_AUDIT — read and execute (verifiy access to all memory read/wrire)
    # API_LINK_AUDIT — read and execute (test each verified api alert if access not allowed)
    # BOT_AUDIT — read and execute (check bot output for timestamps (ensure it is acitive) and errors, alert is not in verified state)
    # TOOL_AUDIT — read and execute (verifiy access to installed tools)
]