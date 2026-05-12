import os
from tools.toolbox import get_toolbox


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")

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
    return f"=== SOUL ===\n{load_md('SOUL.md')}\n\n=== IDENTITY ===\n{load_md('IDENTITY.md')}"
    
# Load and return agent toolbox
def load_toolbox():
    return get_toolbox()