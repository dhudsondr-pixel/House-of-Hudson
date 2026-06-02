"""HTTP client that ships audio to the MedScribe server and returns the note."""
from __future__ import annotations

from pathlib import Path

import httpx


def scribe(server_url: str, audio_path: Path, timeout_s: float = 600.0) -> dict:
    """POST the audio file to /api/scribe and return the parsed JSON response.

    The response contains: transcript, note, timings.
    """
    with audio_path.open("rb") as f:
        files = {"audio": (audio_path.name, f, "audio/wav")}
        r = httpx.post(f"{server_url}/api/scribe", files=files,
                       timeout=httpx.Timeout(timeout_s))
    r.raise_for_status()
    return r.json()
