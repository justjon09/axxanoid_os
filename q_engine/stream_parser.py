import sys
import re
from typing import Tuple

async def parse_tools_from_message(message: str) -> Tuple[list[str]]:
    """
    Extracts tool calls from agent messages.
    """
    tool_calls = re.findall(r'```json\n(.*?)\n```', message, re.DOTALL | re.IGNORECASE)
    return tool_calls
    

async def parse_and_route_stream(async_generator) -> Tuple[str, str, list[str]]:
    """
    1. Streams the raw matrix directly to the Dev Terminal.
    2. Extracts text inside <speak> tags for the UI.
    3. Extracts text inside <tool> tags for backend execution.
    """
    raw_text = ""

    # 1. Print the live stream to the terminal
    async for chunck in async_generator:
        sys.stdout.write(chunck)
        sys.stdout.flush()
        raw_text += chunck

    print("\n") # Clean newline when finished

    # 2. Parse inbound stream text using Regex
    # This specifically hunts for <speak> content </speak> across multiple lines
    speak_match = re.findall(r'<speak>(.*?)</speak>', raw_text, re.DOTALL | re.IGNORECASE)
    
    untagged_text = re.sub(r"<think>(.*?)</think>", "", raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
    untagged_text = re.sub(r"<speak>(.*?)</speak>", "", untagged_text, flags=re.DOTALL | re.IGNORECASE).strip()

    speak_text = ""

    if speak_match:
        # Extract the UI Chat text
        # Tags Found. Strip leading/trailing whitespaces for a clean UI output.
        for speak in speak_match:
            speak_text += f"\n{speak.strip()}"

    if not speak_text:
        # Fallback in case Dolphin respone is not in the system prompted format.
        speak_text = untagged_text if untagged_text else "*(System Error: No Visible Response Found. See Terminal)*"

    return raw_text, speak_text