import asyncio
from typing import AsyncGenerator
from ollama import AsyncClient

# The default prot for local Ollama
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "q_daemon"

async def stream_agent_response(user_promt: str, system_context: str = "", agent: str = "") -> AsyncGenerator[str, None]:
    """
    Streams the response token by token.
    """
    client = AsyncClient(host=OLLAMA_HOST)

    message = [
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_promt}
    ]

    try: 
        # Stream=True is critical. Allows parsing the <think> tags in real-time (Enhancement)
        async for part in await client.chat(
            model=agent if agent else MODEL_NAME,
            messages=message,
            stream=True
        ):
            yield part['message']['content']
    except Exception as e:
        yield f"\n[SYSTEM ERROR: failed to connect to Ollama. Is the model running? Details: {str(e)}]"