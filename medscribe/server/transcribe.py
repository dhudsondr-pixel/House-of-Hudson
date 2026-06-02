"""faster-whisper wrapper. Loads the large-v3 model once and reuses it."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel

_MODEL: Optional[WhisperModel] = None


def get_model() -> WhisperModel:
    """Lazy-load Whisper large-v3 on first call. Stays resident in VRAM."""
    global _MODEL
    if _MODEL is None:
        # float16 on CUDA — fastest accurate option on a 5090.
        # int8_float16 is even faster but slightly less accurate; swap if VRAM
        # is a problem when running the LLM concurrently.
        _MODEL = WhisperModel(
            "large-v3",
            device="cuda",
            compute_type="float16",
        )
    return _MODEL


def transcribe_file(audio_path: Path) -> str:
    """Transcribe an audio file and return a single transcript string."""
    model = get_model()
    segments, info = model.transcribe(
        str(audio_path),
        language="en",
        vad_filter=True,                       # drops silence
        vad_parameters={"min_silence_duration_ms": 500},
        beam_size=5,
        condition_on_previous_text=False,      # avoids hallucination loops
    )
    lines = []
    for seg in segments:
        # mm:ss timestamps help the LLM attribute exchanges later when we add
        # diarisation. For now they make the transcript easier to debug.
        mm = int(seg.start) // 60
        ss = int(seg.start) % 60
        lines.append(f"[{mm:02d}:{ss:02d}] {seg.text.strip()}")
    return "\n".join(lines)
