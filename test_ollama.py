import asyncio
import sys
from q_engine.ollama_client import stream_q_response

async def main():
    # We explicitly ask Q to use both tags to see if he obeys the structure
    prompt = (
        "Q, I need to test your output formatting. "
        "Please calculate 15 * 12. "
        "Show your math strictly inside <think> tags. "
        "Then, provide your final answer strictly inside <speak> tags."
    )
    
    print(f"\n>>> Sending prompt to Dolphin 3.0: '{prompt}'")
    print("-" * 50)
    
    async for chunk in stream_q_response(prompt):
        sys.stdout.write(chunk)
        sys.stdout.flush()
        
    print("\n" + "-" * 50)
    print(">>> Stream complete.")

if __name__ == "__main__":
    asyncio.run(main())