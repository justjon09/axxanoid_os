import os
import sys
import asyncio
from sqlalchemy.orm import Session
from memory.database import SessionLocal
from memory.models import SystemConfig, CurrentChat
from q_engine.ollama_client import stream_q_response
from q_engine.stream_parser import parse_and_route_stream

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

        chat_history = "=== RECENT CHAT LOGS (Last 20 messages) ===\n"
        if not recent_chats:
            chat_history += "No recent conversation history found.\n"
        else:
            # Reverse to put them in chronological order for Dolphin
            for chat in reversed(recent_chats):
                chat_history += f"[{chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {chat.sender.upper()}: {chat.message}\n"


        # 6. Proactive Inference
        print(">>> [HEARTBEAT] Compiling reality and consulting Q...")

        # Compile the baseline
        system_context = f"""
        === CORE DIRECTIVE: SOUL ===
        {soul_md}
        
        === CORE DIRECTIVE: IDENTITY ===
        {identity_md}
        
        === THE HUMAN (MON CAPITAINE) ===
        {human_md}
        """

        # The internal prompt injected into Q's mind every heartbeat
        heartbeat_prompt = (
            f"{chat_history}\n\n"
            "SYSTEM WAKE EVENT: This is your automated background heartbeat. "
            "You are currently running silently in the background. Review the recent chat logs above. "
            "1. Did the human leave any tasks unfinished? "
            "2. Based on the 60-day runway and $20k debt, is the human currently distracted by 'Wood Gathering'? "
            "3. Do you need to execute any background memory organization? "
            "If no action is needed, output exactly: <think>System nominal. No action required.</think><speak>NOMINAL</speak>. "
            "If you must proactively alert the human to an error or inefficiency, use your <speak> tags."
        )

        async def run_subconscious ():
            raw_output = ""
            # Stream subconscious process to the terminal
            async for chunk in stream_q_response(heartbeat_prompt, system_context=system_context):
                sys.stdout.write(chunk)
                sys.stdout.flush()
                raw_output += chunk
            print("\n" + "-" * 50)
            return raw_output
        
        # Execute the stream
        q_response = asyncio.run(run_subconscious())

        # TODO: parse q_response here to auto-save <speak> text to SQLite 

        print(">>> [HEARTBEAT] Audit complete. Releasing RAM and returning to sleep.")
    
    except Exception as e:
        print(f">>> [HEARTBEAT FATAL] {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_heartbeat()