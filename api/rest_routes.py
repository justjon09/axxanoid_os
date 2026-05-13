import sys
import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ollama import AsyncClient
from memory.database import get_db
from memory.models import SystemConfig, CronState, CurrentChat
from memory.vector_store import get_memory_topics
from api.schemas import ChatRequest
from api.utility import load_core_directives, load_toolbox

router = APIRouter()
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
    The main UI chat endpoint.
    """
    print(f"\n>>> [UI REQUEST] User: {request.message}")
    print(">>> [Q ENGINE] Generating thought process ...\n")

    full_prompt = [{"role": "system", "content": GLOBAL_SYSTEM_CONTEXT}]

    # Save the users message to the database
    user_msg = CurrentChat(
        conversation_id=request.conversation_id,
        sender="user",
        message=request.message
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    recent_chats = db.query(CurrentChat).filter(
        CurrentChat.conversation_id == request.conversation_id
    ).order_by(CurrentChat.id.desc()).limit(20).all()

    for chat in reversed(recent_chats):
        if chat.id != user_msg.id: # Skip the message we just inserted
            mapped_role = "assistant" if chat.sender == "q" else "user"
            full_prompt.append({"role": mapped_role, "content": chat.message})

    full_prompt.append({"role": request.sender, "content":request.message}),

    toolbox = load_toolbox()
    client = AsyncClient(host="http://localhost:11434")
    chat = client.chat

    while True:
        # Start the async AI generator and pass the raw python functions
        stream = await chat (
            model="q_daemon", 
            messages=full_prompt,
            stream=True,
            tools=toolbox.values()
        )

        content = ''
        tool_calls = []

        # Accumulate the partial fields
        async for chunk in stream:
            # Handle SDK versioning differences (Dict vs Object)
            msg_content = chunk['message']['content'] if isinstance(chunk, dict) else chunk.message.content

            if msg_content:
                content += msg_content
                sys.stdout.write(msg_content)
                sys.stdout.flush()

        if content:
            msg_tools = parse_tools_from_message(content)
            if msg_tools:
                tool_calls.extend(msg_tools)
                print(f"\n === TOOLs ===\n{tool_calls}")
            full_prompt.append({'role': 'assistant', 'content': content, 'tool_calls': tool_calls})

        # Break the loop if agent didn't ask for a tool
        if not tool_calls:
            break
        
        for tool_call in tool_calls:
            # Extract the raw name and dict arguments
            func_name = tool_call['function']['name'] if isinstance(tool_call, dict) else tool_call.function.name
            args = tool_call['function']['arguments'] if isinstance(tool_call, dict) else tool_call.function.arguments

            print(f"\n>>> [TOOL INJECTION][TOOL REQUEST]{func_name}...")

            tool_func = toolbox.get(func_name)

            if tool_func:
                try:
                    # **args safely unpacks the dictionary natively into the tool's parameters
                    # asyncio.to_thread prevents the synchronous DB query from freezing FastAPI
                    tool_result = await asyncio.to_thread(tool_func, **args)
                    print(f">>> [TOOL INJECTION] [TOOL RESULT] {str(tool_result)[:150]}...\n")
                except Exception as e:
                    print(f">> [TOOL INJECTION] [TOOL EXECUTION ERROR] {str(e)}")
                    tool_result = f"Execution Error: {str(e)}"
            else:
                print(f">> [TOOL INJECTION] [TOOL ERROR] {func_name} not an availble tool")
                tool_result = "Unknown Tool Error"

            # Inject the python result back into his active context window
            full_prompt.append({'role': 'tool', 'name': func_name, 'content': str(tool_result)})
    
    # Save cleaned response to database
    agent_msg = CurrentChat(
        conversation_id=request.conversation_id,
        sender="assistant",
        message=content
    )
    db.add(agent_msg)
    db.commit()
    db.refresh(agent_msg)

    return {
        "status": "success",
        "q_response": content
    }