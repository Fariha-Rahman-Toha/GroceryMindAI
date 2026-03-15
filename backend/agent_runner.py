"""
agent_runner.py
For azure-ai-projects 2.0.1
Bypasses AIProjectClient entirely.
Uses AzureOpenAI directly with API key — works everywhere, no az login needed.
"""

import time
import traceback
from openai import AzureOpenAI
from config import AZURE_OPENAI_ENDPOINT, AZURE_AI_API_KEY


def run_agent(agent_id: str, user_message: str, timeout: int = 300) -> str:

    print(f"\n{'='*60}")
    print(f"[runner] Agent   : {agent_id}")
    print(f"[runner] Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"[runner] Message : {user_message[:100]}")
    print(f"{'='*60}")

    if not AZURE_OPENAI_ENDPOINT:
        return "ERROR: AZURE_OPENAI_ENDPOINT not set in .env"
    if not AZURE_AI_API_KEY:
        return "ERROR: AZURE_AI_API_KEY not set in .env"
    if not agent_id or agent_id in ("asst_xxxxx", "", None):
        return "ERROR: Agent ID missing or placeholder in .env"

    try:
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_AI_API_KEY,
            api_version="2024-05-01-preview",
        )
        print("[runner] AzureOpenAI client created")
    except Exception as e:
        print(traceback.format_exc())
        return f"ERROR: Failed to create client — {str(e)}"

    try:
        # Create thread
        print("[runner] Creating thread...")
        thread = client.beta.threads.create()
        print(f"[runner] Thread: {thread.id}")

        # Add message
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )
        print("[runner] Message added")

        # Create run
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=agent_id,
        )
        print(f"[runner] Run: {run.id} | Status: {run.status}")

        # Poll until done
        start = time.time()
        count = 0
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            count += 1
            elapsed = round(time.time() - start, 1)
            print(f"[runner] Poll #{count:03d} | {run.status:20s} | {elapsed}s")

            if run.status == "completed":
                print(f"[runner] Done in {elapsed}s")
                break
            if run.status in ("failed", "cancelled", "expired"):
                return f"ERROR: Run {run.status} — {getattr(run, 'last_error', 'no detail')}"
            if run.status == "requires_action":
                return "ERROR: requires_action — check agent tool configuration in AI Foundry"
            if time.time() - start > timeout:
                return f"ERROR: Timed out after {timeout}s. Last status: {run.status}"
            time.sleep(3)

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for msg in messages.data:
            if msg.role == "assistant":
                for block in msg.content:
                    if hasattr(block, "text"):
                        text = block.text.value
                        print(f"[runner] Response: {len(text)} chars")
                        return text

        return "ERROR: Run completed but no response found"

    except Exception as e:
        print(traceback.format_exc())
        return f"ERROR: Exception — {str(e)}"