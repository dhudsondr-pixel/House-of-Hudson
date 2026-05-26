"""Word search grid generator. Places words in 8 directions with collision checking."""
from __future__ import annotations

import random
import string
from typing import Dict, List, Tuple

DIRECTIONS = [
    ( 0,  1, "right"),
    ( 0, -1, "left"),
    ( 1,  0, "down"),
    (-1,  0, "up"),
    ( 1,  1, "down-right"),
    ( 1, -1, "down-left"),
    (-1,  1, "up-right"),
    (-1, -1, "up-left"),
]


def _try_place(grid: List[List[str]], word: str, r: int, c: int, dr: int, dc: int) -> bool:
    rows = len(grid)
    cols = len(grid[0])
    positions: List[Tuple[int, int]] = []
    for i, ch in enumerate(word):
        nr, nc = r + dr * i, c + dc * i
        if not (0 <= nr < rows and 0 <= nc < cols):
            return False
        cell = grid[nr][nc]
        if cell not in ("", ch):
            return False
        positions.append((nr, nc))
    for (nr, nc), ch in zip(positions, word):
        grid[nr][nc] = ch
    return True


def generate(words: List[str], size: int = 15, max_attempts_per_word: int = 200, seed: int | None = None) -> dict:
    """Generate a square word-search grid.

    Returns:
        {"grid": [[char,...],...], "positions": {WORD: {"row":r, "col":c, "dir": name}}}
    Words that can't be placed are dropped (we keep going to deliver a complete grid).
    """
    rng = random.Random(seed)
    grid = [["" for _ in range(size)] for _ in range(size)]
    positions: Dict[str, Dict] = {}

    # Place longest words first — better packing.
    words_sorted = sorted(set(w.upper() for w in words), key=len, reverse=True)

    for word in words_sorted:
        if len(word) > size:
            continue
        placed = False
        for _ in range(max_attempts_per_word):
            r = rng.randrange(size)
            c = rng.randrange(size)
            dr, dc, name = rng.choice(DIRECTIONS)
            if _try_place(grid, word, r, c, dr, dc):
                positions[word] = {"row": r, "col": c, "dir": name}
                placed = True
                break
        # If not placed, just skip.
        _ = placed

    # Fill empty cells with random letters.
    for r in range(size):
        for c in range(size):
            if grid[r][c] == "":
                grid[r][c] = rng.choice(string.ascii_uppercase)

    return {"grid": grid, "positions": positions}
