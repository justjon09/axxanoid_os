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
        # TODO: Run audits based on config HEARTBEAT.md - Run audits:


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
            #TODO: use config HEARTBEAT.md - Heartbeat Prompt List Items:
            "1. Did the human leave any tasks unfinished? "
            "2. Based on the $1k per week income floor, is the human currently distracted by 'Wood Gathering'? "
            "3. Do you need to execute any background memory organization? "
            "If no action is needed, output exactly: <think>System nominal. No action required.</think><speak>NOMINAL</speak>. "
            "If you must proactively alert the human to an error or inefficiency, use your <speak> tags."
        )

        async def run_subconscious ():
            # Pass the generator to existing parser
            generator = stream_q_response(heartbeat_prompt, system_context=system_context)
            raw_text, clean_text = await parse_and_route_stream(generator)
            return raw_text, clean_text
        
        # Execute the stream
        raw_text, clean_text = asyncio.run(run_subconscious())

        # Parse q_response to auto-save <speak> text to SQLite
        # If Q output "NOMINAL", we do nothing. If he spoke, we save it to the DB.
        if clean_text and "NOMINAL" not in clean_text:
            print("\n [HEARTBEAT] Proactive action triggered. Routing alert to UI....")

            # Attach the current conversation ID or default to 1
            active_convo_id = recent_chats[0].conversation_id if recent_chats else 1

            proactive_alert = CurrentChat(
                conversation_id=active_convo_id,
                sender="q",
                message=clean_text
            )
            db.add(proactive_alert)
            db.commit()
            db.refresh(proactive_alert)
        else:
            print("\n >>>[HEARTBEAT] System Nominal. No proactive alerts generated")
        print(">>> [HEARTBEAT] Audit complete. Releasing RAM and returning to sleep.")
    
    except Exception as e:
        print(f">>> [HEARTBEAT FATAL] {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_heartbeat()