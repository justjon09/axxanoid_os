import sys
import re
from typing import Tuple

async def parse_and_route_stream(async_generator) -> Tuple[str, str]:
    """
    1. Streams the raw matrix directly to the Dev Terminal.
    2. Extracts ONLY the text inside <speak> tags for the UI/Database.
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
    speak_match = re.search(r'<speak>(.*?)</speak>', raw_text, re.DOTALL | re.IGNORECASE)

    # This specifically hunts for <tool> content </tool> across multiple lines
    tool_match = re.search(r'<tool>(.*?)</tool>', raw_text, re.DOTALL | re.IGNORECASE)

    if tool_match:
        # Extract the Tool Request for processing
        # Tags Found. Strip leading/trailing whitespaces
        tool_request = tool_match.group(1).strip()


    if speak_match:
        # Extract the UI Chat text
        # Tags Found. Strip leading/trailing whitespaces for a clean UI output.
        speach_text = speak_match.group(1).strip()
    else:
        # Fallback in case Dolphin respone is not in the system prompted format.
        # Pull <think> and retrun remaing content
        fallback_text = re.sub(r"<think>(.*?)</think>", "", raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
        speach_text = fallback_text if fallback_text else "*(System Error: No Visible Response Found. See Terminal)*"
    return raw_text, speach_text