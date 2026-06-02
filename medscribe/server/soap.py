"""Generate the SOAP note from a transcript by calling a local Ollama LLM."""
from __future__ import annotations

from pathlib import Path

import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:32b-instruct-q4_K_M"

_PROMPT_PATH = Path(__file__).parent / "prompts" / "soap_au_gp.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()


async def generate_soap(transcript: str) -> str:
    """Send the transcript through the AU-GP SOAP prompt and return the note."""
    prompt = _PROMPT_TEMPLATE.replace("{{transcript}}", transcript)

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            # Low temperature: clinical notes need to be deterministic and
            # faithful to the transcript, not creative.
            "temperature": 0.2,
            "top_p": 0.9,
            # Big context for long consults. Qwen 2.5 supports up to 128k.
            "num_ctx": 16384,
        },
    }

    async with httpx.AsyncClient(timeout=600.0) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
        data = r.json()
    return data["message"]["content"]
