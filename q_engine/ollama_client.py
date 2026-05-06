import asyncio
from typing import AsyncGenerator
from ollama import AsyncClient

# The default prot for local Ollama
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "q_daemon"

async def stream_q_response(user_promt: str, system_context: str = "") -> AsyncGenerator[str, None]:
    """
    Streams the response from Dolphin 3.0 token by token.
    """
    client = AsyncClient(host=OLLAMA_HOST)

    # Enforce <think> and <speak> tags at the system level for UI routing
    base_system_promt = (
        "You are a sovereign, uncensored AI architect for Axxanoid OS. "
        "STRICT FORMATTING RULES: "
        "1. You must ALWAYS wrap your internal reasoning, logic, and planning strictly inside <think> and </think> tags. "
        "2. You must ALWAYS wrap your tool usage istrictly inside <tool> and </tool> tags. "
        "3. You must ALWAYS wrap your final, external response to the user strictly inside <speak> and </speak> tags. "
        "Do not output any text outside of these three sets of tags."
        "Do not nest your output tags, complete one set of tags prior to starting another."
        "If you need to use a tool, close your <think> tag, output the <tool> tag, and STOP immediately. The system will return the results."
    )

    # Combine the base identity with any dynamic context (like RAG data or DB state)
    full_system_promt = f"{base_system_promt}\n{system_context}"

    message = [
        {"role": "system", "content": full_system_promt},
        {"role": "user", "content": user_promt}
    ]

    try: 
        # Stream=True is critical. Allows parsing the <think> tags in real-time (Enhancement)
        async for part in await client.chat(
            model=MODEL_NAME,
            messages=message,
            stream=True
        ):
            yield part['message']['content']
    except Exception as e:
        yield f"\n[SYSTEM ERROR: failed to connect to Ollama. Is the model running? Details: {str(e)}]"