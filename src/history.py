"""Track which topics have already been generated to avoid repeats."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


def load(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def save(path: Path, topics: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(topics, indent=2))
