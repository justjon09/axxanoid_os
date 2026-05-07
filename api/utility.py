import os
import re
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
TOOL_DIR = os.path.join(BASE_DIR, "tools")

# Load Markdown files into RAM on request
def load_md(filename):
    filepath = os.path.join(CONFIG_DIR, filename)
    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"[System Note: {filename} missing]"
    
# Load and return Markdown files
def load_core_directives() -> str:   
    return f"=== SOUL ===\n{load_md('SOUL.md')}\n\n=== IDENTITY ===\n{load_md('IDENTITY.md')}\n\n=== THE HUMAN ===\n{load_md('HUMAN.md')}\n\n=== TOOLS ===\n{load_md('TOOLS.md')}"
    
# Process Single Agent Tool Request
async def execute_requested_tool(tool_request: str) -> str:
    """
    Parses agents tool request syntax. Routes to correct modular Python script.
    """
    tool_request = tool_request.strip()
    tool_request_args = re.findall(r"\[(.*?)\]", tool_request)
    tool_request_name = tool_request_args[0] if tool_request_args else None
    tool_output = ""
    tools_list = []
    tools_md = load_md("TOOLS.md")
    
    # Parse Availble Tools List Items
    availble_tools_match = re.search(r"Available Tools:\s*\[(.*?)\]:End Availble Tools", tools_md, re.DOTALL)

    if availble_tools_match:
        tool_box = availble_tools_match.group(1)
        # Extract each individual { ... } block first
        tool_blocks = re.findall(r"\{(.*?)\}", tool_box, re.DOTALL)
        for block in tool_blocks:
            # Extract the name and script strictly from within this block
            name_match = re.search(r"name:\s*(.*?),", block)
            script_match = re.search(r"script:\s*(.*?),", block)
            if name_match and script_match:
                tools_list.append({
                    "name": name_match.group(1).strip(),
                    "script": script_match.group(1).strip(),
                })

    if tool_request_name in [tool["name"] for tool in tools_list]:
        tool_to_use = next((tool for tool in tools_list if tool["name"] == tool_request_name), None)
        if tool_to_use:
            script_name = tool_to_use["script"]
            script_path = os.path.join(TOOL_DIR, script_name)
            
            if os.path.exists(script_path):
                try:
                    # Run the script as a subprocess in the current venv
                    result = subprocess.run(
                        [sys.executable, script_path, *tool_request_args[1:]],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=10
                    )
                    if result.stderr:
                        tool_output += f"[TOOL ERROR: {tool_to_use['name']} - {result.stderr.strip()}]"
                    else:
                        tool_output += result.stdout.strip()
                except Exception as e:
                   tool_output += f"[TOOL ERROR: {tool_to_use['name']} -  {str(e)}]"
            else:
                tool_output += f"[TOOL ERROR: {tool_to_use['name']} - Script not found at {script_path}]"
        else:
            tool_output += f"[TOOL REQUEST ERROR: {tool_request_name} not availble tool]"
    return tool_output
