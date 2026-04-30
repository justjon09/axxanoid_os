import os
import sys
from sqlalchemy.orm import Session
from memory.database import SessionLocal
from memory.models import SystemConfig, CurrentChat

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")

def load_directive(filename: str) -> str:
    """Reads markdown files safely in RAM. Prevents fatal crash is file not found."""
    filepath = os.path.join(CONFIG_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f">>> [HEARTBEAT WARNING] Missing directive file: {filename}. Skipping.")
        return f"[System Note: {filename} is currently missing or inaccessible.]"

def run_heartbeat():
    # Instantiate DB session
    db: Session = SessionLocal()

    try:
        # 1. UI Control Check (The Killswitch)
        heartbeat_config = db.query(SystemConfig).first()
        if not heartbeat_config or not heartbeat_config.cron_active:
            print(">>> [HEARTBEAT] Cron is disabled via system congig setting.")
            return
        
        # 2. State Collision Check
        if heartbeat_config.q_status in ["thinking", "executing"]:
            print(f">>> [HEARTBEAT] Q is currently {heartbeat_config.q_status}. Skipping heartbeat to protect VRAM.")
            return
        

        print(">>> [HEARTBEAT] Wake sequence initiated. Ingesting core directives into RAM...")
        
        # 3. RAM Loading (Identity & Directives)
        soul_md = load_directive("SOUL.md")
        identity_md = load_directive("IDENTITY.md")
        human_md = load_directive("HUMAN.md")

        # 4. System Audit (verify self)
        # TODO: Run audits for apis, tools, heardware, and/or bots againt known configs
        # HARDWARE_AUDIT— read and execute (compare actuall availbe hardware to known hardware configuration alert if not matching) 
        # API_LINK_AUDIT — read and execute (test each verified api alert if access not allowed)
        # BOT_AUDIT — read and execute (check bot output for timestamps (ensure it is acitive) and errors, alert is not in verified state)
        # TOOL_AUDIT — read and execute (verifiy access to installed tools)

        # 5. Chat Audit (Short-Term Memory Pull)
        # Grab the last 20 messages to see what happened since the last heartbeat
        recent_chats = db.query(CurrentChat).order_by(CurrentChat.id.desc()).limit(20).all()

        # 6. Proactive Inference
        # TODO: Compile directives + recent chats into a prompt.
        # Send to Dolphin 3: "Review the last 30 minutes. Are there tasks to execute or memories to compact?"

        print(">>> [HEARTBEAT] Audit complete. Releasing RAM and returning to sleep.")
    
    except Exception as e:
        print(f">>> [HEARTBEAT FATAL] {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_heartbeat()