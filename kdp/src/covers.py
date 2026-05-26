"""KDP wrap cover generator (single PDF: back + spine + front, with bleed)."""
from __future__ import annotations

import hashlib
import textwrap
from pathlib import Path
from typing import List, Tuple

from reportlab.lib.colors import Color
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from .specs import BLEED, TRIM_SIZES, cover_dimensions


# Curated palettes. Each: bg (background), accent (lines), title (text), sub (subtitle/secondary).
# Color tuples are 0-255 RGB.
PALETTES = [
    # Bold / productivity
    {"name": "navy_gold",  "bg": (12, 27, 51),    "accent": (212, 175, 55), "title": (255, 255, 255), "sub": (220, 200, 130)},
    {"name": "forest",     "bg": (33, 64, 47),    "accent": (235, 215, 169), "title": (245, 240, 230), "sub": (235, 215, 169)},
    {"name": "plum",       "bg": (54, 30, 60),    "accent": (240, 192, 95),  "title": (250, 245, 240), "sub": (240, 192, 95)},
    {"name": "charcoal",   "bg": (28, 28, 30),    "accent": (250, 200, 50),  "title": (255, 255, 255), "sub": (245, 215, 110)},
    # Soft / self-care
    {"name": "sage",       "bg": (203, 217, 195), "accent": (90, 100, 80),   "title": (40, 50, 35),    "sub": (90, 100, 80)},
    {"name": "blush",      "bg": (235, 207, 207), "accent": (140, 70, 80),   "title": (50, 25, 30),    "sub": (140, 70, 80)},
    {"name": "cream",      "bg": (244, 234, 213), "accent": (130, 90, 50),   "title": (60, 40, 25),    "sub": (130, 90, 50)},
    {"name": "dusty_blue", "bg": (180, 200, 215), "accent": (45, 65, 95),    "title": (25, 40, 65),    "sub": (60, 80, 110)},
    # Activity / energetic
    {"name": "tomato",     "bg": (200, 60, 50),   "accent": (255, 220, 140), "title": (255, 255, 255), "sub": (255, 220, 140)},
    {"name": "teal",       "bg": (40, 110, 120),  "accent": (255, 220, 150), "title": (255, 255, 255), "sub": (255, 220, 150)},
]

TITLE_FONTS = ["Helvetica-Bold", "Times-Bold"]
SUB_FONTS   = ["Helvetica", "Times-Italic"]
BODY_FONTS  = ["Helvetica", "Times-Roman"]


def _rgb(t: Tuple[int, int, int]) -> Color:
    return Color(t[0] / 255, t[1] / 255, t[2] / 255)


def _deterministic_choice(seed: str, options: list):
    return options[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(options)]


def _fit_text(c: canvas.Canvas, text: str, font: str, max_size: int, min_size: int,
              max_width_pt: float, max_lines: int = 4) -> Tuple[List[str], int, float]:
    """Find the largest font size at which the text fits, possibly across multiple lines.

    Constraints: lines must fit horizontally AND there must be no more than
    `max_lines` lines at the chosen size. If text simply won't fit at min_size,
    it's truncated word-by-word until it does (with a trailing "...").

    Returns (wrapped_lines, font_size, total_height_pt).
    """
    text = text.strip()

    for size in range(max_size, min_size - 1, -2):
        avg_char = c.stringWidth("M", font, size) or size * 0.55
        approx_cols = max(8, int(max_width_pt / avg_char))
        wrapped = textwrap.fill(text, width=approx_cols, break_long_words=False).splitlines()
        widest = max((c.stringWidth(line, font, size) for line in wrapped), default=0)
        if widest <= max_width_pt and len(wrapped) <= max_lines:
            leading = size * 1.15
            total_h = leading * (len(wrapped) - 1) + size
            return wrapped, size, total_h

    # Couldn't fit even at min_size — truncate the text until it fits.
    avg_char = c.stringWidth("M", font, min_size) or min_size * 0.55
    approx_cols = max(6, int(max_width_pt / avg_char))
    words = text.split()
    while words:
        candidate = " ".join(words)
        if len(words) < len(text.split()):
            candidate += "..."
        wrapped = textwrap.fill(candidate, width=approx_cols, break_long_words=False).splitlines()
        widest = max((c.stringWidth(line, font, min_size) for line in wrapped), default=0)
        if widest <= max_width_pt and len(wrapped) <= max_lines:
            leading = min_size * 1.15
            return wrapped, min_size, leading * (len(wrapped) - 1) + min_size
        words = words[:-1]

    # Truly degenerate (single huge word) — return as-is at min size.
    leading = min_size * 1.15
    return [text], min_size, min_size


def _draw_text_block(c: canvas.Canvas, lines: List[str], font: str, size: int,
                     color: Color, cx: float, top_y: float, leading_mult: float = 1.15) -> float:
    """Draw a block of centered lines. `top_y` is the top edge (cap height) of the first line.
    Returns the y-coordinate of the bottom of the last line."""
    c.setFont(font, size)
    c.setFillColor(color)
    leading = size * leading_mult
    baseline = top_y - size  # first baseline is one font-size below top edge
    for line in lines:
        c.drawCentredString(cx, baseline, line)
        baseline -= leading
    bottom = baseline + leading - size  # bottom of last drawn line
    return bottom


def build_cover(
    title: str,
    subtitle: str,
    author: str,
    back_blurb: str,
    trim: str,
    page_count: int,
    paper: str,
    out_path: Path,
    style_seed: str | None = None,
) -> Path:
    full_w, full_h, spine_w = cover_dimensions(trim, page_count, paper)
    trim_w, trim_h = TRIM_SIZES[trim]
    page_size_pt = (full_w * 72, full_h * 72)

    seed = style_seed or title
    palette = _deterministic_choice(seed, PALETTES)
    title_font = _deterministic_choice(seed + "tf", TITLE_FONTS)
    sub_font   = _deterministic_choice(seed + "sf", SUB_FONTS)
    body_font  = _deterministic_choice(seed + "bf", BODY_FONTS)

    bg     = _rgb(palette["bg"])
    accent = _rgb(palette["accent"])
    t_col  = _rgb(palette["title"])
    s_col  = _rgb(palette["sub"])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=page_size_pt)

    # Background fills entire wrap including bleed.
    c.setFillColor(bg)
    c.rect(0, 0, page_size_pt[0], page_size_pt[1], fill=1, stroke=0)

    # Wrap layout: [BLEED][back: trim_w][spine: spine_w][front: trim_w][BLEED] horizontally.
    back_x0  = BLEED * 72
    back_x1  = back_x0 + trim_w * 72
    spine_x0 = back_x1
    spine_x1 = spine_x0 + spine_w * 72
    front_x0 = spine_x1
    front_x1 = front_x0 + trim_w * 72  # == full_w - BLEED

    # Safe inner padding from trim edges (keeps text inside the live area).
    inner_pad = 0.5 * 72
    # Text-safe vertical boundaries for the front cover (in points).
    front_top_safe    = (BLEED + trim_h - 0.5) * 72       # 0.5" below top trim
    front_bottom_safe = (BLEED + 0.5) * 72                 # 0.5" above bottom trim

    # ---- FRONT COVER ----
    front_cx = (front_x0 + front_x1) / 2
    front_text_w = trim_w * 72 - inner_pad * 2

    # 1. Title — sits in upper-middle of front cover. Top edge at 88% of trim height.
    title_top = front_bottom_safe + (front_top_safe - front_bottom_safe) * 0.85
    title_lines, title_size, title_h = _fit_text(c, title.upper(), title_font,
                                                  max_size=58, min_size=22, max_width_pt=front_text_w,
                                                  max_lines=4)
    title_bottom = _draw_text_block(c, title_lines, title_font, title_size, t_col, front_cx, title_top)

    # 2. Accent rule below title.
    rule_y = title_bottom - 18
    c.setStrokeColor(accent)
    c.setLineWidth(2.0)
    rule_half = front_text_w * 0.35
    c.line(front_cx - rule_half, rule_y, front_cx + rule_half, rule_y)

    # 3. Subtitle — sits below accent rule.
    if subtitle:
        sub_top = rule_y - 20
        sub_lines, sub_size, sub_h = _fit_text(c, subtitle, sub_font,
                                                max_size=22, min_size=12, max_width_pt=front_text_w * 0.95)
        _draw_text_block(c, sub_lines, sub_font, sub_size, s_col, front_cx, sub_top)

    # 4. Author at bottom.
    if author:
        c.setFont(body_font, 18)
        c.setFillColor(t_col)
        c.drawCentredString(front_cx, front_bottom_safe + 6, author)
        # Thin accent rule above author.
        c.setStrokeColor(accent)
        c.setLineWidth(0.8)
        au_rule_half = front_text_w * 0.2
        au_rule_y = front_bottom_safe + 28
        c.line(front_cx - au_rule_half, au_rule_y, front_cx + au_rule_half, au_rule_y)

    # ---- BACK COVER ----
    back_cx = (back_x0 + back_x1) / 2
    back_text_w = trim_w * 72 - inner_pad * 2

    if back_blurb:
        blurb_top = (BLEED + trim_h - 1.2) * 72
        blurb_lines, blurb_size, blurb_h = _fit_text(c, back_blurb, body_font,
                                                     max_size=14, min_size=9, max_width_pt=back_text_w)
        # Cap to a reasonable number of lines so we don't fill the back with tiny text.
        max_lines = 18
        if len(blurb_lines) > max_lines:
            blurb_lines = blurb_lines[:max_lines]
            blurb_lines[-1] = blurb_lines[-1].rstrip(".,;: ") + "..."
        _draw_text_block(c, blurb_lines, body_font, blurb_size, t_col, back_cx, blurb_top)

    if author:
        c.setFont(body_font, 11)
        c.setFillColor(s_col)
        c.drawCentredString(back_cx, front_bottom_safe + 6, f"by {author}")

    # ---- SPINE ----
    # Only add spine text if spine is thick enough (~0.3" minimum recommended by KDP).
    if spine_w >= 0.3:
        spine_cx = (spine_x0 + spine_x1) / 2
        spine_cy = full_h * 72 / 2
        c.saveState()
        c.translate(spine_cx, spine_cy)
        c.rotate(90)
        spine_text_max = full_h * 72 - 1 * 72
        spine_text = title.upper()
        if author:
            spine_text = f"{title.upper()}   ·   {author}"
        spine_size = 14
        while spine_size > 7 and c.stringWidth(spine_text, title_font, spine_size) > spine_text_max:
            spine_size -= 1
        c.setFont(title_font, spine_size)
        c.setFillColor(t_col)
        c.drawCentredString(0, -spine_size / 3, spine_text)
        c.restoreState()

    c.showPage()
    c.save()
    return out_path
