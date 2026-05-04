import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from q_engine.ollama_client import stream_q_response
from q_engine.stream_parser import parse_and_route_stream
from memory.database import get_db
from memory.models import SystemConfig, CronState, ChatLogs, CurrentChat
from memory.vector_store import get_memory_topics
from api.schemas import ChatRequest

router = APIRouter()


# Load Markdown files into RAM once when FastAPI boots.
def load_core_directives() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, "config")
    
    def load_md(filename):
        filepath = os.path.join(config_dir, filename)
        try:
            with open(filepath, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return f"[System Note: {filename} missing]"
            
    return f"=== SOUL ===\n{load_md('SOUL.md')}\n\n=== IDENTITY ===\n{load_md('IDENTITY.md')}\n\n=== THE HUMAN ===\n{load_md('HUMAN.md')}"

GLOBAL_SYSTEM_CONTEXT = load_core_directives()

@router.get("/system/status")
async def get_system_status(db: Session = Depends(get_db)):
    """Fetches the current global configuration and Q's state"""
    config = db.query(SystemConfig).first()
    if not config:
        # Auto-initialize the first row if the database is brand new
        config = SystemConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.post("/system/toggle-heartbeat")
async def toggle_heartbeat(db: Session = Depends(get_db)):
    """Allows the UI to turn Q's autonomous heartbeat on or off."""
    config = db.query(SystemConfig).first()
    if config:
        config.cron_active = not config.cron_active
        db.commit()
        db.refresh(config)
        return {"status": "success", "cron_active": config.cron_active}
    return {"status": "error", "message": "System config not initialized"}

@router.get("/cron/state")
async def get_all_crons(db: Session = Depends(get_db)):
    """Returns the list of all background jobs and their last run status."""
    return db.query(CronState).all()

@router.post("/cron/toggle/{job_name}")
async def toggle_cron_job(job_name: str, db: Session = Depends(get_db)):
    """Allows the UI to turn cron jobs on or off."""
    cron_job = db.query(CronState).filter(CronState.job_name == job_name).first()
    if cron_job:
        cron_job.enabled = not cron_job.enabled
        db.commit()
        db.refresh(cron_job)
        return {"status": "success", "enabled": cron_job.enabled}
    return {"status": "error", "message": "Cron job not found"}

@router.get("/memory/topics")
async def fetch_memory_topics():
    """Allows the UI to see what topics exist in Q's long-term vector memory."""
    topics = get_memory_topics()
    return {"status": "success", "topics": topics}

# The schma defining what the UI will send to Python
@router.post("/chat")
async def chat_via_ui(request: ChatRequest, db: Session = Depends(get_db)):
    """
    The main UI chat endpoint. UI sends a message -> Python receives -> Saves to database -> Sends to dolphin(Q) as prompt -> dolphin(Q) streams response -> Python routes response: Thinking to terminal, Speaking cleaned and sent to UI and datebase.
    """
    print(f"\n>>> [UI REQUEST] User: {request.message}")
    print(">>> [Q ENGINE] Generating thought process ...\n")

    # 1. Save the users message to the database
    user_msg = CurrentChat(
        conversation_id=request.conversation_id,
        sender="user",
        message=request.message
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 1.5 Fetch Short-Term Memory (20 messages)
    recent_chats = db.query(CurrentChat).filter(
        CurrentChat.conversation_id == request.conversation_id
    ).order_by(CurrentChat.id.desc()).limit(20).all()
    chat_history = ""
    # Reverse to chronological order
    for chat in reversed(recent_chats):
        if chat.id != user_msg.id: # Skip the message we just inserted
            chat_history += f"{chat.sender.upper()}: {chat.message}\n"

    # Compile the prompt with the history
    full_prompt = f"=== RECENT CHAT HISTORY ===\n{chat_history}\n\nUSER: {request.message}" if chat_history else request.message

    # 2. Start the AI generator 
    raw_generator = stream_q_response(full_prompt, system_context=GLOBAL_SYSTEM_CONTEXT)

    # 3. Pass the gernerator through parser - Terminal sees all live
    raw_text, clean_text = await parse_and_route_stream(raw_generator)

    # 4. Save cleaned response to database
    q_msg = CurrentChat(
        conversation_id=request.conversation_id,
        sender="q",
        message=clean_text
    )
    db.add(q_msg)
    db.commit()
    db.refresh(q_msg)

    return {
        "status": "success",
        "q_response": clean_text
    }