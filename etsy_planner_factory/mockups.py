"""Etsy product image (mockup) generator.

Etsy requires/prefers 2000x2000px square images. The first image is the
most important — buyers scroll past anything ugly. We generate three
mockups per product:
  1. Hero — bold title card with the planner name and theme.
  2. Preview — a clean 'sheet on background' showing the layout.
  3. Listing card — bullet list of what's included.
"""

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .themes import Theme


CANVAS = 2000  # square


def _rgb255(c):
    return tuple(int(round(v * 255)) for v in c)


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    # Use PIL's bundled default; fall back-safe across systems.
    try:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                return ImageFont.truetype(c, size)
    except Exception:
        pass
    return ImageFont.load_default(size=size)


def _text_centered(draw, xy_box, text, font, fill, max_width=None):
    x0, y0, x1, y1 = xy_box
    # Word wrap if needed
    if max_width:
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width and cur:
                lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)
    else:
        lines = [text]

    # Compute total height
    line_h = font.size + 8
    total_h = line_h * len(lines)
    y = y0 + ((y1 - y0) - total_h) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = x0 + ((x1 - x0) - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h


def hero(theme: Theme, planner_name: str, out_path: str) -> None:
    img = Image.new("RGB", (CANVAS, CANVAS), _rgb255(theme.background))
    d = ImageDraw.Draw(img)

    # Decorative band
    band_h = 380
    d.rectangle([0, CANVAS - band_h, CANVAS, CANVAS], fill=_rgb255(theme.primary))

    # Title block
    big = _font(180, bold=True)
    small = _font(72, bold=False)

    _text_centered(d, (200, 300, CANVAS - 200, 900),
                   planner_name.upper(), big, _rgb255(theme.text),
                   max_width=CANVAS - 400)
    _text_centered(d, (200, 920, CANVAS - 200, 1100),
                   "PRINTABLE  ·  INSTANT DOWNLOAD",
                   small, _rgb255(theme.secondary))

    # Bottom band text
    bb = _font(64, bold=True)
    _text_centered(d, (0, CANVAS - band_h, CANVAS, CANVAS),
                   theme.display_name.upper(),
                   bb, _rgb255(theme.background))

    img.save(out_path, "PNG", optimize=True)


def preview(theme: Theme, planner_name: str, out_path: str) -> None:
    """A stylized 'sheet on background' that mimics the planner layout."""
    img = Image.new("RGB", (CANVAS, CANVAS), _rgb255(theme.secondary))
    d = ImageDraw.Draw(img)

    # Paper rectangle, centered, with shadow
    paper_w = 1400
    paper_h = 1800
    px = (CANVAS - paper_w) // 2
    py = (CANVAS - paper_h) // 2
    # Shadow
    d.rectangle([px + 24, py + 24, px + paper_w + 24, py + paper_h + 24],
                fill=(0, 0, 0, 60))
    # Paper
    d.rectangle([px, py, px + paper_w, py + paper_h],
                fill=_rgb255(theme.background))

    # Title bar on the paper
    title_f = _font(96, bold=True)
    d.text((px + 80, py + 80), planner_name.upper(),
           font=title_f, fill=_rgb255(theme.primary))
    d.line([px + 80, py + 200, px + 80 + 240, py + 200],
           fill=_rgb255(theme.primary), width=8)

    # Mock content lines
    line_color = _rgb255(theme.muted)
    for i in range(18):
        y = py + 320 + i * 78
        d.line([px + 80, y, px + paper_w - 80, y],
               fill=line_color, width=3)

    # Mock checkboxes (left column)
    for i in range(6):
        y = py + 320 + i * 78
        d.rectangle([px + 80, y - 36, px + 130, y - 4],
                    outline=line_color, width=3)

    img.save(out_path, "PNG", optimize=True)


def card(theme: Theme, planner_name: str, bullets: list[str],
         out_path: str) -> None:
    img = Image.new("RGB", (CANVAS, CANVAS), _rgb255(theme.background))
    d = ImageDraw.Draw(img)

    title_f = _font(110, bold=True)
    body_f = _font(64, bold=False)

    d.text((140, 160), "WHAT YOU GET",
           font=_font(60, bold=True), fill=_rgb255(theme.secondary))
    d.text((140, 240), planner_name.upper(),
           font=title_f, fill=_rgb255(theme.primary))
    d.line([140, 380, 460, 380], fill=_rgb255(theme.primary), width=10)

    y = 520
    for b in bullets:
        d.ellipse([140, y + 18, 180, y + 58], fill=_rgb255(theme.primary))
        d.text((220, y), b, font=body_f, fill=_rgb255(theme.text))
        y += 130

    img.save(out_path, "PNG", optimize=True)
