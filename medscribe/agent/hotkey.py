"""Global hotkey listener using pynput. Works on Windows (Win32 hook), macOS
(Quartz), and X11 Linux. On Wayland, the keystroke may be blocked by the
compositor — document the workaround in the README.
"""
from __future__ import annotations

from typing import Callable

from pynput import keyboard


class GlobalHotkey:
    def __init__(self, combo: str, on_trigger: Callable[[], None]) -> None:
        self.combo = combo
        self.on_trigger = on_trigger
        self._listener: keyboard.GlobalHotKeys | None = None

    def start(self) -> None:
        self._listener = keyboard.GlobalHotKeys({self.combo: self.on_trigger})
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
