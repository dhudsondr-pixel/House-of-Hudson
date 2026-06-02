"""Persistent agent config. Stored in ~/.medscribe.json (cross-platform)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

CONFIG_PATH = Path.home() / ".medscribe.json"


@dataclass
class AgentConfig:
    # Server that runs Whisper + Ollama. Defaults to localhost for the dev box;
    # beta GPs point this at the inference server (e.g. http://192.168.x.x:8080
    # over LAN, or http://your-tailscale-hostname:8080 over VPN).
    server_url: str = "http://localhost:8080"

    # Audio input device. None = system default; otherwise the sounddevice
    # device index (int) or name fragment (str, e.g. "Yealink").
    mic_device: str | int | None = None

    # Global hotkey for start/stop. pynput format.
    # Examples: "<f8>", "<ctrl>+<alt>+r", "<f9>"
    hotkey: str = "<f8>"

    # Sample rate for recording (Hz). 16000 is Whisper-native; speakerphones
    # commonly run at 48000 and ffmpeg downsamples.
    sample_rate: int = 16000

    # Auto-copy generated note to clipboard.
    auto_copy: bool = True

    # Show desktop notification when note is ready.
    show_notification: bool = True


def load() -> AgentConfig:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            return AgentConfig(**{k: v for k, v in data.items()
                                  if k in AgentConfig.__dataclass_fields__})
        except (json.JSONDecodeError, TypeError):
            pass
    return AgentConfig()


def save(cfg: AgentConfig) -> None:
    CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2))
