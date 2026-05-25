"""Pinterest pin renderer. Output: 1000x1500 PNG + a sidecar caption .txt."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw

from . import render

PIN_W = 1000
PIN_H = 1500


def _draw_bold_pin(
    hook: str,
    subhead: str,
    brand: str,
    palette: tuple,
    seed: str,
) -> Image.Image:
    bg, accent, text, muted = palette
    img = render.textured_background((PIN_W, PIN_H), bg, accent, seed)
    draw = ImageDraw.Draw(img)

    # Big hook in upper-middle.
    max_w = int(PIN_W * 0.85)
    hook_font, hook_lines = render.fit_text(render.load_bold, hook.upper(), max_w, max_size=130, min_size=56)
    block_h = sum(hook_font.getbbox(l)[3] - hook_font.getbbox(l)[1] for l in hook_lines) + 12 * (len(hook_lines) - 1)
    top_y = (PIN_H - block_h) // 2 - 40
    after_y = render.draw_centered_block(draw, hook_lines, hook_font, text, PIN_W // 2, top_y, line_gap=12)

    # Accent rule.
    rule_y = after_y + 30
    rule_half = int(PIN_W * 0.18)
    draw.line([(PIN_W // 2 - rule_half, rule_y), (PIN_W // 2 + rule_half, rule_y)], fill=accent, width=4)

    # Subhead.
    if subhead:
        sub_font, sub_lines = render.fit_text(render.load_serif, subhead, int(PIN_W * 0.7), max_size=44, min_size=22)
        render.draw_centered_block(draw, sub_lines, sub_font, muted, PIN_W // 2, rule_y + 30, line_gap=8)

    # Brand mark at bottom.
    if brand:
        brand_font = render.load_regular(28)
        bbox = brand_font.getbbox(brand)
        bw = bbox[2] - bbox[0]
        draw.text(((PIN_W - bw) // 2, PIN_H - 80), brand, font=brand_font, fill=accent)

    return img


def _draw_quote_pin(
    hook: str,
    subhead: str,
    brand: str,
    palette: tuple,
    seed: str,
) -> Image.Image:
    bg, accent, text, muted = palette
    img = render.textured_background((PIN_W, PIN_H), bg, accent, seed + "q")
    draw = ImageDraw.Draw(img)

    # Decorative quotes.
    qf = render.load_serif(220)
    draw.text((90, 130), "“", font=qf, fill=(*accent[:3],))

    # Quote text centered.
    max_w = int(PIN_W * 0.78)
    quote_font, quote_lines = render.fit_text(render.load_serif, hook, max_w, max_size=78, min_size=32)
    block_h = sum(quote_font.getbbox(l)[3] - quote_font.getbbox(l)[1] for l in quote_lines) + 14 * (len(quote_lines) - 1)
    render.draw_centered_block(draw, quote_lines, quote_font, text, PIN_W // 2,
                                (PIN_H - block_h) // 2, line_gap=14)

    # Subhead/attribution.
    if subhead:
        sub_font = render.load_regular(28)
        bbox = sub_font.getbbox(subhead)
        sw = bbox[2] - bbox[0]
        draw.text(((PIN_W - sw) // 2, int(PIN_H * 0.78)), subhead.upper(), font=sub_font, fill=muted)

    if brand:
        brand_font = render.load_regular(26)
        bbox = brand_font.getbbox(brand)
        bw = bbox[2] - bbox[0]
        draw.text(((PIN_W - bw) // 2, PIN_H - 80), brand, font=brand_font, fill=accent)

    return img


def _draw_tip_pin(hook: str, subhead: str, brand: str, palette: tuple, seed: str) -> Image.Image:
    """Top band with 'TIP' label, then big text body."""
    bg, accent, text, muted = palette
    img = Image.new("RGB", (PIN_W, PIN_H), bg)
    draw = ImageDraw.Draw(img)

    # Top accent band.
    band_h = int(PIN_H * 0.14)
    draw.rectangle((0, 0, PIN_W, band_h), fill=accent)
    label_font = render.load_bold(40)
    label = "TODAY'S PRACTICE"
    bbox = label_font.getbbox(label)
    lw = bbox[2] - bbox[0]
    lh = bbox[3] - bbox[1]
    # Choose readable color on accent band.
    label_color = bg if (sum(accent) < 380) else text
    draw.text(((PIN_W - lw) // 2, (band_h - lh) // 2 - 4), label, font=label_font, fill=label_color)

    # Main hook in middle.
    max_w = int(PIN_W * 0.85)
    hook_font, hook_lines = render.fit_text(render.load_bold, hook, max_w, max_size=110, min_size=52)
    block_h = sum(hook_font.getbbox(l)[3] - hook_font.getbbox(l)[1] for l in hook_lines) + 14 * (len(hook_lines) - 1)
    render.draw_centered_block(draw, hook_lines, hook_font, text, PIN_W // 2,
                                (PIN_H - block_h) // 2 + 30, line_gap=14)

    # Subhead small italic-style below.
    if subhead:
        sub_font, sub_lines = render.fit_text(render.load_serif, subhead, int(PIN_W * 0.72),
                                               max_size=36, min_size=18)
        block_h2 = sum(sub_font.getbbox(l)[3] - sub_font.getbbox(l)[1] for l in sub_lines) + 8 * (len(sub_lines) - 1)
        render.draw_centered_block(draw, sub_lines, sub_font, muted, PIN_W // 2,
                                    int(PIN_H * 0.78) - block_h2 // 2, line_gap=8)

    # Brand at bottom.
    if brand:
        brand_font = render.load_regular(28)
        bbox = brand_font.getbbox(brand)
        bw = bbox[2] - bbox[0]
        draw.text(((PIN_W - bw) // 2, PIN_H - 80), brand, font=brand_font, fill=accent)

    return img


def _draw_listicle_pin(hook: str, subhead: str, brand: str, palette: tuple, seed: str) -> Image.Image:
    """Numbered list style — uses subhead as comma-or-pipe-separated items."""
    bg, accent, text, muted = palette
    img = render.textured_background((PIN_W, PIN_H), bg, accent, seed + "l")
    draw = ImageDraw.Draw(img)

    # Hook at top.
    max_w = int(PIN_W * 0.85)
    hook_font, hook_lines = render.fit_text(render.load_bold, hook.upper(), max_w, max_size=80, min_size=42)
    top_y = int(PIN_H * 0.12)
    after_y = render.draw_centered_block(draw, hook_lines, hook_font, text, PIN_W // 2, top_y, line_gap=10)

    # Divider.
    rule_y = after_y + 30
    rule_half = int(PIN_W * 0.18)
    draw.line([(PIN_W // 2 - rule_half, rule_y), (PIN_W // 2 + rule_half, rule_y)], fill=accent, width=4)

    # List items from subhead.
    items = [s.strip() for s in subhead.replace("|", ",").split(",") if s.strip()]
    if not items:
        items = [subhead] if subhead else []
    item_font = render.load_regular(40)
    num_font = render.load_bold(56)
    y = rule_y + 50
    for i, item in enumerate(items[:5], 1):
        # Number.
        num_str = f"{i:02d}"
        draw.text((PIN_W * 0.12, y), num_str, font=num_font, fill=accent)
        # Wrap item text.
        item_lines = render.wrap_to_width(item_font, item, int(PIN_W * 0.7))
        for line in item_lines:
            draw.text((PIN_W * 0.26, y + 8), line, font=item_font, fill=text)
            y += 50
        y += 30

    if brand:
        brand_font = render.load_regular(28)
        bbox = brand_font.getbbox(brand)
        bw = bbox[2] - bbox[0]
        draw.text(((PIN_W - bw) // 2, PIN_H - 80), brand, font=brand_font, fill=accent)

    return img


STYLES = {
    "bold":     _draw_bold_pin,
    "quote":    _draw_quote_pin,
    "tip":      _draw_tip_pin,
    "listicle": _draw_listicle_pin,
}


def build_pin(
    hook: str,
    subhead: str,
    style: str,
    brand: str,
    seed: str,
    palette_keys: list | None = None,
) -> Image.Image:
    palette = render.palette_for(seed, allowed=palette_keys)
    fn = STYLES.get(style, _draw_bold_pin)
    return fn(hook, subhead, brand, palette, seed)


def write_caption(
    path: Path,
    hook: str,
    description: str,
    hashtags: list,
    link_in_bio: str,
    title_field: str | None = None,
) -> Path:
    """Write the Pinterest sidecar (title + description + hashtags + URL)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    title = (title_field or hook)[:100]
    desc = description.strip()
    if len(desc) > 500:
        desc = desc[:497] + "..."
    body = [
        "=== Pinterest Pin ===",
        "",
        f"Pin title (max 100 chars):",
        title,
        "",
        "Pin description (paste into Pinterest's 'Description' field):",
        desc,
        "",
        "Hashtags (Pinterest allows them in description):",
        " ".join(hashtags),
        "",
        f"Destination URL (paste into 'Destination link'):",
        link_in_bio,
    ]
    path.write_text("\n".join(body))
    return path
