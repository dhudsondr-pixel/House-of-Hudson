"""Audio recorder using sounddevice. Captures raw PCM, writes WAV on stop.

Designed for USB speakerphones (Yealink CP700, Jabra Speak, etc.) on the
GP's desk. Picks the configured device by name fragment or index, falling
back to the system default.
"""
from __future__ import annotations

import queue
import tempfile
import threading
import wave
from pathlib import Path

import sounddevice as sd


SPEAKERPHONE_HINTS = ("yealink", "jabra", "speak", "anker powerconf",
                      "conferencecam", "poly sync", "voyager")


def list_input_devices() -> list[dict]:
    """Return all audio input devices with their indices and names."""
    out = []
    for i, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0:
            out.append({
                "index": i,
                "name": dev["name"],
                "default_sample_rate": int(dev["default_samplerate"]),
                "is_speakerphone": any(h in dev["name"].lower()
                                       for h in SPEAKERPHONE_HINTS),
            })
    return out


def resolve_device(mic: str | int | None) -> int | None:
    """Resolve a device hint (None / int / name fragment) to a device index."""
    if mic is None:
        return None
    if isinstance(mic, int):
        return mic
    needle = mic.lower()
    for dev in list_input_devices():
        if needle in dev["name"].lower():
            return dev["index"]
    return None


class Recorder:
    """Threaded mic recorder. start() returns immediately; stop() flushes WAV."""

    def __init__(self, sample_rate: int = 16000,
                 device: str | int | None = None) -> None:
        self.sample_rate = sample_rate
        self.device_index = resolve_device(device)
        self._q: queue.Queue = queue.Queue()
        self._stream: sd.InputStream | None = None
        self._is_recording = False

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def _callback(self, indata, frames, time_info, status) -> None:
        if status:
            # Overflow / underflow — log but don't crash the consult.
            pass
        self._q.put(indata.copy())

    def start(self) -> None:
        if self._is_recording:
            return
        # Drain stale audio.
        while not self._q.empty():
            try: self._q.get_nowait()
            except queue.Empty: break
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            device=self.device_index,
            channels=1,
            dtype="int16",
            callback=self._callback,
        )
        self._stream.start()
        self._is_recording = True

    def stop(self) -> Path:
        """Stop and write the recording to a temp WAV. Returns the path."""
        if not self._is_recording or self._stream is None:
            raise RuntimeError("not recording")
        self._stream.stop()
        self._stream.close()
        self._stream = None
        self._is_recording = False

        # Flush queue into a WAV file.
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        path = Path(tmp.name)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            while not self._q.empty():
                wf.writeframes(self._q.get().tobytes())
        return path
