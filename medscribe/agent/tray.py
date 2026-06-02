"""System tray icon + menu. Right-click for settings, click to record."""
from __future__ import annotations

import threading
from typing import Callable

import pystray
from PIL import Image, ImageDraw


def _make_icon(color: str) -> Image.Image:
    """Generate a simple coloured circle PNG for the tray."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill=color)
    return img


ICONS = {
    "idle":       _make_icon("#2f5d4f"),  # green
    "recording":  _make_icon("#b54848"),  # red
    "processing": _make_icon("#d4a73a"),  # amber
    "error":      _make_icon("#6b6b6b"),  # grey
}


class Tray:
    """Thin wrapper around pystray. Single icon, menu items injected by main."""

    def __init__(self,
                 on_toggle_record: Callable[[], None],
                 on_show_settings: Callable[[], None],
                 on_quit: Callable[[], None]) -> None:
        self._on_toggle_record = on_toggle_record
        self._on_show_settings = on_show_settings
        self._on_quit_cb = on_quit
        self._icon: pystray.Icon | None = None

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Start / stop (or press hotkey)",
                             lambda: self._on_toggle_record()),
            pystray.MenuItem("Settings…", lambda: self._on_show_settings()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda: self._quit()),
        )

    def _quit(self) -> None:
        self._on_quit_cb()
        if self._icon:
            self._icon.stop()

    def set_state(self, state: str) -> None:
        if self._icon is None:
            return
        self._icon.icon = ICONS.get(state, ICONS["idle"])
        self._icon.title = f"MedScribe — {state}"

    def run(self) -> None:
        self._icon = pystray.Icon(
            "medscribe",
            ICONS["idle"],
            "MedScribe — idle",
            menu=self._build_menu(),
        )
        self._icon.run()  # blocking; call from main thread
