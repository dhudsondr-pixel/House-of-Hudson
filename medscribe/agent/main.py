"""MedScribe desktop agent.

Sits in the system tray. Press the global hotkey (default F8) to start a
recording, press it again to stop. Audio is sent to the local MedScribe
server (FastAPI + Whisper + Ollama), and the resulting SOAP note is
copied to the clipboard with a notification.

Run with:  python -m medscribe.agent.main

For first-time setup:  python -m medscribe.agent.main --list-devices
"""
from __future__ import annotations

import argparse
import sys
import threading
import traceback

from . import config as cfg_mod
from .client import scribe
from .hotkey import GlobalHotkey
from .notify import copy_to_clipboard, notify
from .recorder import Recorder, list_input_devices
from .tray import Tray


def cmd_list_devices() -> None:
    print("Audio input devices:")
    print(f"  {'idx':>4}  {'name':<48}  rate    speakerphone?")
    print(f"  {'-'*4}  {'-'*48}  ------  ------")
    for d in list_input_devices():
        mark = "  ★" if d["is_speakerphone"] else ""
        print(f"  {d['index']:>4}  {d['name'][:48]:<48}  "
              f"{d['default_sample_rate']:>5}  {mark}")
    print()
    print("Set the chosen mic in ~/.medscribe.json:")
    print('  {"mic_device": "Yealink"}     # name fragment')
    print('  {"mic_device": 3}             # device index')


class Agent:
    """Wires the tray, hotkey, recorder, and HTTP client together."""

    def __init__(self) -> None:
        self.cfg = cfg_mod.load()
        self.recorder = Recorder(sample_rate=self.cfg.sample_rate,
                                 device=self.cfg.mic_device)
        self.tray = Tray(
            on_toggle_record=self.toggle_record,
            on_show_settings=self.show_settings,
            on_quit=self.shutdown,
        )
        self.hotkey = GlobalHotkey(self.cfg.hotkey, self.toggle_record)

    # ----- recording lifecycle -----

    def toggle_record(self) -> None:
        if self.recorder.is_recording:
            self.stop_and_process()
        else:
            self.start_recording()

    def start_recording(self) -> None:
        try:
            self.recorder.start()
            self.tray.set_state("recording")
        except Exception as e:
            notify("MedScribe error", f"Mic failed: {e}")
            self.tray.set_state("error")

    def stop_and_process(self) -> None:
        self.tray.set_state("processing")
        try:
            audio_path = self.recorder.stop()
        except Exception as e:
            notify("MedScribe error", f"Stop failed: {e}")
            self.tray.set_state("error")
            return
        # Process in a background thread so the tray stays responsive.
        threading.Thread(target=self._process_audio, args=(audio_path,),
                         daemon=True).start()

    def _process_audio(self, audio_path) -> None:
        try:
            result = scribe(self.cfg.server_url, audio_path)
            note = result.get("note", "")
            timings = result.get("timings", {})
            if self.cfg.auto_copy and note:
                copy_to_clipboard(note)
            if self.cfg.show_notification:
                t_msg = (f"transcribed in {timings.get('transcribe_s', '?')}s, "
                         f"note in {timings.get('soap_s', '?')}s")
                notify("MedScribe — SOAP note ready",
                       f"Copied to clipboard. {t_msg}")
            self.tray.set_state("idle")
        except Exception:
            traceback.print_exc()
            notify("MedScribe error", "Server call failed. See terminal.")
            self.tray.set_state("error")
        finally:
            try: audio_path.unlink(missing_ok=True)
            except Exception: pass

    # ----- settings & shutdown -----

    def show_settings(self) -> None:
        """Print current config + how to edit it. UI deferred to v0.3."""
        notify(
            "MedScribe settings",
            f"Server: {self.cfg.server_url}\n"
            f"Mic: {self.cfg.mic_device or 'system default'}\n"
            f"Hotkey: {self.cfg.hotkey}\n"
            f"Edit ~/.medscribe.json to change."
        )

    def shutdown(self) -> None:
        self.hotkey.stop()
        if self.recorder.is_recording:
            try: self.recorder.stop()
            except Exception: pass

    # ----- entrypoint -----

    def run(self) -> None:
        self.hotkey.start()
        notify("MedScribe ready",
               f"Press {self.cfg.hotkey} to start a consult recording.")
        self.tray.run()  # blocking


def main() -> None:
    parser = argparse.ArgumentParser(prog="medscribe-agent")
    parser.add_argument("--list-devices", action="store_true",
                        help="Print audio input devices and exit")
    args = parser.parse_args()

    if args.list_devices:
        cmd_list_devices()
        return

    Agent().run()


if __name__ == "__main__":
    main()
