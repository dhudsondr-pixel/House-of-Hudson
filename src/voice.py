"""Generate voiceover audio from text using free Google TTS."""
from __future__ import annotations

from pathlib import Path

from gtts import gTTS

VOICE_MAP = {
    "en-us-female": ("en", "us"),
    "en-us-male":   ("en", "us"),    # gTTS doesn't expose male/female; same accent
    "en-uk-female": ("en", "co.uk"),
    "en-uk-male":   ("en", "co.uk"),
    "en-au-female": ("en", "com.au"),
    "en-au-male":   ("en", "com.au"),
}


def synthesize(text: str, voice: str, out_path: Path) -> Path:
    lang, tld = VOICE_MAP.get(voice, ("en", "us"))
    tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tts.save(str(out_path))
    return out_path
