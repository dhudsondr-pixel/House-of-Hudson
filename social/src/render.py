"""Shared image rendering helpers for social posts (Pillow-based)."""
from __future__ import annotations

import hashlib
import textwrap
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont


# Palettes hand-picked for each "style". Each: bg, accent, text, muted.
PALETTES = {
    # Maker / industrial / tech (good for 3D printing brand content)
    "industrial": [(28, 28, 30),    (245, 123, 0),   (250, 248, 240), (170, 160, 150)],  # charcoal + orange
    "blueprint":  [(15, 50, 85),    (235, 240, 250), (250, 250, 255), (165, 190, 220)],  # navy + white
    "midnight":   [(14, 18, 32),    (212, 175, 55),  (250, 245, 235), (180, 165, 130)],  # midnight + gold
    "neon":       [(16, 16, 24),    (125, 249, 255), (250, 250, 255), (140, 200, 215)],  # black + cyan
    "molten":     [(196, 90, 60),   (255, 220, 160), (255, 245, 230), (250, 210, 170)],  # warm rust + cream
    "lab":        [(232, 235, 240), (35, 60, 110),   (20, 30, 50),    (115, 130, 160)],  # off-white + cobalt
    "graphite":   [(46, 48, 54),    (200, 200, 205), (245, 245, 250), (130, 135, 145)],  # graphite + silver
    "circuit":    [(15, 35, 30),    (90, 215, 145),  (235, 250, 240), (130, 175, 150)],  # dark green + mint
}


def palette_for(seed: str, allowed: List[str] | None = None) -> Tuple[Tuple[int, int, int], ...]:
    keys = list(PALETTES.keys()) if not allowed else [k for k in PALETTES if k in allowed]
    if not keys:
        keys = list(PALETTES.keys())
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return tuple(PALETTES[keys[h % len(keys)]])


# Font hunting (same approach as the video gen tool).
FONT_PATHS_BOLD = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:\\Windows\\Fonts\\impact.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]
FONT_PATHS_SERIF = [
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "C:\\Windows\\Fonts\\georgia.ttf",
    "C:\\Windows\\Fonts\\times.ttf",
]
FONT_PATHS_REG = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
]


def _load(paths: list, size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def load_bold(size: int) -> ImageFont.FreeTypeFont:
    return _load(FONT_PATHS_BOLD, size)


def load_serif(size: int) -> ImageFont.FreeTypeFont:
    return _load(FONT_PATHS_SERIF, size)


def load_regular(size: int) -> ImageFont.FreeTypeFont:
    return _load(FONT_PATHS_REG, size)


def wrap_to_width(font: ImageFont.FreeTypeFont, text: str, max_w: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        bbox = font.getbbox(trial)
        if (bbox[2] - bbox[0]) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(loader, text: str, max_w: int, max_size: int, min_size: int) -> Tuple[ImageFont.FreeTypeFont, List[str]]:
    """Find the largest font size at which text wraps acceptably (<=4 lines by default)."""
    for size in range(max_size, min_size - 1, -2):
        font = loader(size)
        lines = wrap_to_width(font, text, max_w)
        widths = [font.getbbox(l)[2] - font.getbbox(l)[0] for l in lines]
        if max(widths, default=0) <= max_w and len(lines) <= 5:
            return font, lines
    font = loader(min_size)
    return font, wrap_to_width(font, text, max_w)


def draw_centered_block(
    draw: ImageDraw.ImageDraw,
    lines: List[str],
    font: ImageFont.FreeTypeFont,
    color: Tuple[int, int, int],
    cx: int,
    top_y: int,
    line_gap: int = 8,
    stroke_w: int = 0,
    stroke_fill: Tuple[int, int, int] | None = None,
) -> int:
    """Draw centered multi-line text. Returns the y-coordinate after the block."""
    y = top_y
    for line in lines:
        bbox = font.getbbox(line)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = cx - line_w // 2
        kwargs = {"font": font, "fill": color}
        if stroke_w > 0 and stroke_fill is not None:
            kwargs["stroke_width"] = stroke_w
            kwargs["stroke_fill"] = stroke_fill
        draw.text((x, y), line, **kwargs)
        y += line_h + line_gap
    return y


def textured_background(
    size: Tuple[int, int],
    bg: Tuple[int, int, int],
    accent: Tuple[int, int, int],
    seed: str,
) -> Image.Image:
    """Solid-color bg with a subtle accent shape, deterministic per seed."""
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    w, h = size
    h_int = int(hashlib.md5(seed.encode()).hexdigest(), 16)

    variant = h_int % 4
    accent_alpha = Image.new("RGBA", size, (0, 0, 0, 0))
    ad = ImageDraw.Draw(accent_alpha)
    a = (*accent, 40)  # very subtle

    if variant == 0:
        # Soft circle in top-right.
        r = min(w, h) // 2
        ad.ellipse((w - r, -r // 2, w + r // 2, r), fill=a)
    elif variant == 1:
        # Diagonal band.
        ad.polygon([(0, h * 0.6), (w, h * 0.4), (w, h * 0.55), (0, h * 0.75)], fill=a)
    elif variant == 2:
        # Bottom-left arc.
        r = min(w, h)
        ad.ellipse((-r // 3, h - r // 2, r, h + r // 3), fill=a)
    else:
        # Centered thin frame.
        m = min(w, h) // 18
        ad.rectangle((m, m, w - m, h - m), outline=(*accent, 80), width=3)

    accent_alpha = accent_alpha.filter(ImageFilter.GaussianBlur(radius=3))
    img.paste(accent_alpha, (0, 0), accent_alpha)
    return img


def save_png(img: Image.Image, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)
    return path
