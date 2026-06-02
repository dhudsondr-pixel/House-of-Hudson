"""Cross-platform desktop notifications + clipboard. Thin wrappers that
fail silently if a platform-specific backend is missing."""
from __future__ import annotations


def notify(title: str, body: str) -> None:
    try:
        from plyer import notification
        notification.notify(title=title, message=body, app_name="MedScribe",
                            timeout=5)
    except Exception:
        # Fall back to stdout if no GUI notification backend is available.
        print(f"[notify] {title}: {body}")


def copy_to_clipboard(text: str) -> None:
    try:
        import pyperclip
        pyperclip.copy(text)
    except Exception as e:
        print(f"[clipboard] failed: {e}")
