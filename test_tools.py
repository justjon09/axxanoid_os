import os
import re
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
TOOL_DIR = os.path.join(BASE_DIR, "tools")

def load_md(filename):
    filepath = os.path.join(CONFIG_DIR, filename)
    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
    
def get_tool_tests_list():
    test_list = []
    tools_md = load_md("TOOLS.md")
    availble_tools_match = re.search(r"Available Tools:\s*\[(.*?)\]:End Availble Tools", tools_md, re.DOTALL)
    
    if availble_tools_match:
        tool_box = availble_tools_match.group(1)
        tool_blocks = re.findall(r"\{(.*?)\}", tool_box, re.DOTALL)
        for block in tool_blocks:
            name_match = re.search(r"name:\s*(.*?),", block)
            tests_match = re.search(r"tests:\s*\[(.*?)\]:End Tests", block, re.DOTALL)
            if name_match and tests_match:
                for test in tests_match.group(1).strip().split(","):
                    test_list.append({
                        "name": name_match.group(1).strip(),
                        "test": test.strip()
                    })
    return test_list
    
def test_tool_execution(tool_request: str):
    """
    Replicates the exact logic in rest_routes.py
    """
    print(f"\n[TESTING ROUTE] -> {tool_request}")
    tool_request = tool_request.strip()
    tool_request_args = re.findall(r"\[(.*?)\]", tool_request)
    tool_request_name = tool_request_args[0] if tool_request_args else None
    
    tools_list = []
    tools_md = load_md("TOOLS.md")
    
    # 1. Parse TOOLS.md
    availble_tools_match = re.search(r"Available Tools:\s*\[(.*?)\]:End Availble Tools", tools_md, re.DOTALL)
    if availble_tools_match:
        tool_box = availble_tools_match.group(1)
        tool_blocks = re.findall(r"\{(.*?)\}", tool_box, re.DOTALL)
        for block in tool_blocks:
            name_match = re.search(r"name:\s*(.*?),", block)
            script_match = re.search(r"script:\s*(.*?),", block)
            if name_match and script_match:
                tools_list.append({
                    "name": name_match.group(1).strip(),
                    "script": script_match.group(1).strip(),
                })
    # 2. Match and Execute
    if tool_request_name in [tool["name"] for tool in tools_list]:
        tool_to_use = next((tool for tool in tools_list if tool["name"] == tool_request_name), None)
        script_path = os.path.join(TOOL_DIR, tool_to_use["script"])
        
        print(f"  -> Found Script: {script_path}")
        print(f"  -> Subprocess Args: {tool_request_args[1:]}")
        
        if os.path.exists(script_path):
            try:
                result = subprocess.run(
                    [sys.executable, script_path, *tool_request_args[1:]],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10
                )
                if result.stderr:
                    print(f"  -> [STDERR (Warnings)]:\n{result.stderr.strip()}")
                if result.stdout:
                    print(f"  -> [STDOUT (Output)]:\n{result.stdout.strip()}")
            except Exception as e:
                print(f"  -> [CRASH]: {str(e)}")
        else:
            print(f"  -> [ERROR]: Script missing at {script_path}")
    else:
        print(f"  -> [ERROR]: {tool_request_name} not found in TOOLS.md")

if __name__ == "__main__":
    print("=== STARTING TOOL AUDIT ===")

    # Gather Test Strings
    tests = get_tool_tests_list()

    if tests:
        for test in tests:
            test_tool_execution(f"{test['test']}")
    
    print("\n=== AUDIT COMPLETE ===")