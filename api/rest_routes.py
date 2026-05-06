import os
import re
import sys
import subprocess
import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from q_engine.ollama_client import stream_q_response
from q_engine.stream_parser import parse_and_route_stream
from memory.database import get_db
from memory.models import SystemConfig, CronState, CurrentChat
from memory.vector_store import get_memory_topics
from api.schemas import ChatRequest

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

router = APIRouter()

# Load Markdown files into RAM once when FastAPI boots.
def load_core_directives() -> str:   
    return f"=== SOUL ===\n{load_md('SOUL.md')}\n\n=== IDENTITY ===\n{load_md('IDENTITY.md')}\n\n=== THE HUMAN ===\n{load_md('HUMAN.md')}\n\n=== TOOLS ===\n{load_md('TOOLS.md')}"

GLOBAL_SYSTEM_CONTEXT = load_core_directives()

# Process Agent Tool Request
def execute_requested_tool(tool_request: str) -> str:
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
    availble_tools_match = re.search(r"Available Tools:\s*\[(.*?)\]", tools_md, re.DOTALL)

    if availble_tools_match:
        lines = availble_tools_match.group(1).strip().split("\n")
        for line in lines:
            clean_line = line.strip()
            # Extract {name: ..., script: ...}
            match = re.search(r'\{name:\s*(.*?), \s*script:\s*(.*?)"\}', clean_line)
            if match:
                tools_list.append({
                    "name": match.group(1).strip(),
                    "script": match.group(2).strip(),
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

    # Save the users message to the database
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
    full_prompt = f"=== RECENT CHAT HISTORY ===\n{chat_history}\n\nUSER: {request.message}" if chat_history else f"USER: {request.message}"

    # THE INTERCEPTOR LOOP
    max_tool_loops = 5 # Prevent infinite tool calling loops
    current_loop = 0
    final_speech = ""

    while current_loop < max_tool_loops:
        # Start the AI generator
        raw_generator = stream_q_response(full_prompt, system_context=GLOBAL_SYSTEM_CONTEXT)
        # Pass the gernerator through parser - Terminal sees all live
        raw_text, speech_text, tool_request = await parse_and_route_stream(raw_generator)

        # If agent output a <tool> tag, intercept and execute it
        if tool_request:
            tool_result = execute_requested_tool(tool_request)
            
            # Print the result to the dev terminal so you see what Q sees
            print(f"\n>>> [TOOL INJECTION] Providing Q with requested data...\n{tool_result}\n")

            # Append the tool usage and the system result to Q's prompt and loop again
            full_prompt += f"\n\n<tool>{tool_request}</tool>\nSYSTEM TOOL RESULT:\n{tool_result}\n\nPlease proceed based on these results."
            current_loop += 1
            continue # Fire again with the new data

        # If no tool was requested, agent is speaking to the user. Break the loop.
        final_speech = speech_text
        break
    # If he hits the limit and still didn't speak, force an error
    if not final_speech:
        final_speech = "*(System Error: Q-Daemon exceeded maximum tool execution depth or failed to output `<speak>` tags.)*"

    # Save cleaned response to database
    q_msg = CurrentChat(
        conversation_id=request.conversation_id,
        sender="q",
        message=final_speech
    )
    db.add(q_msg)
    db.commit()
    db.refresh(q_msg)

    return {
        "status": "success",
        "q_response": final_speech
    }