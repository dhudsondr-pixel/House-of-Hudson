"""Instagram post renderers: single quote (1080x1080) + carousel (1080x1350)."""
from __future__ import annotations

from pathlib import Path
from typing import List

from PIL import Image, ImageDraw

from . import render

SQUARE = (1080, 1080)
PORTRAIT = (1080, 1350)


def build_quote(quote: str, brand: str, seed: str, palette_keys: list | None = None) -> Image.Image:
    palette = render.palette_for(seed, allowed=palette_keys)
    bg, accent, text, muted = palette

    img = render.textured_background(SQUARE, bg, accent, seed + "iq")
    draw = ImageDraw.Draw(img)

    # Decorative open-quote mark.
    qf = render.load_serif(180)
    draw.text((60, 60), "“", font=qf, fill=accent)

    max_w = int(SQUARE[0] * 0.8)
    quote_font, quote_lines = render.fit_text(render.load_serif, quote, max_w, max_size=72, min_size=32)
    block_h = sum(quote_font.getbbox(l)[3] - quote_font.getbbox(l)[1] for l in quote_lines) + 14 * (len(quote_lines) - 1)
    render.draw_centered_block(draw, quote_lines, quote_font, text, SQUARE[0] // 2,
                                (SQUARE[1] - block_h) // 2, line_gap=14)

    if brand:
        brand_font = render.load_regular(26)
        bbox = brand_font.getbbox(brand)
        bw = bbox[2] - bbox[0]
        draw.text(((SQUARE[0] - bw) // 2, SQUARE[1] - 70), brand, font=brand_font, fill=muted)

    return img


def build_carousel(
    hook: str,
    slides: List[dict],
    brand: str,
    seed: str,
    palette_keys: list | None = None,
) -> List[Image.Image]:
    """Returns list of slide images in order (Instagram portrait, 1080x1350)."""
    palette = render.palette_for(seed, allowed=palette_keys)
    bg, accent, text, muted = palette
    W, H = PORTRAIT
    images: List[Image.Image] = []

    # ---- Slide 1: hook ----
    img1 = render.textured_background((W, H), bg, accent, seed + "c1")
    d1 = ImageDraw.Draw(img1)
    # "SWIPE →" tag at top.
    tag_font = render.load_bold(28)
    tag = "SWIPE  →"
    bbox = tag_font.getbbox(tag)
    d1.text((W - 60 - (bbox[2] - bbox[0]), 60), tag, font=tag_font, fill=accent)

    hook_font, hook_lines = render.fit_text(render.load_bold, hook, int(W * 0.85), max_size=108, min_size=48)
    block_h = sum(hook_font.getbbox(l)[3] - hook_font.getbbox(l)[1] for l in hook_lines) + 14 * (len(hook_lines) - 1)
    render.draw_centered_block(d1, hook_lines, hook_font, text, W // 2, (H - block_h) // 2, line_gap=14)
    if brand:
        bf = render.load_regular(26)
        bbox = bf.getbbox(brand)
        d1.text(((W - (bbox[2] - bbox[0])) // 2, H - 80), brand, font=bf, fill=muted)
    images.append(img1)

    # ---- Middle slides ----
    for i, slide in enumerate(slides[:-1] if len(slides) > 1 else slides, 1):
        if i == 1 and len(slides) > 1:
            # Skip — first slide is the hook above. Middle slides start at index 1 from API.
            pass
        img = render.textured_background((W, H), bg, accent, seed + f"c{i+1}")
        d = ImageDraw.Draw(img)

        # Slide number indicator.
        num_font = render.load_regular(22)
        num_text = f"{i:02d} / {len(slides):02d}"
        bbox = num_font.getbbox(num_text)
        d.text((W - 60 - (bbox[2] - bbox[0]), 60), num_text, font=num_font, fill=muted)

        heading = slide.get("heading", "")
        body = slide.get("body", "")

        if heading:
            h_font, h_lines = render.fit_text(render.load_bold, heading, int(W * 0.85),
                                               max_size=92, min_size=44)
            top = int(H * 0.25)
            after = render.draw_centered_block(d, h_lines, h_font, text, W // 2, top, line_gap=10)
            # Accent rule.
            rule_y = after + 30
            d.line([(W // 2 - 80, rule_y), (W // 2 + 80, rule_y)], fill=accent, width=3)
            body_top = rule_y + 40
        else:
            body_top = int(H * 0.4)

        if body:
            b_font, b_lines = render.fit_text(render.load_regular, body, int(W * 0.8),
                                               max_size=44, min_size=22)
            render.draw_centered_block(d, b_lines, b_font, text, W // 2, body_top, line_gap=10)

        if brand:
            bf = render.load_regular(22)
            bbox = bf.getbbox(brand)
            d.text(((W - (bbox[2] - bbox[0])) // 2, H - 70), brand, font=bf, fill=muted)
        images.append(img)

    # ---- Final CTA slide ----
    if len(slides) >= 1:
        final = slides[-1]
        img_final = Image.new("RGB", (W, H), accent)
        df = ImageDraw.Draw(img_final)

        heading = final.get("heading", "Find it on Amazon")
        body = final.get("body", "")
        text_on_accent = bg if sum(accent) < 380 else text

        h_font, h_lines = render.fit_text(render.load_bold, heading, int(W * 0.85),
                                           max_size=88, min_size=42)
        block_h = sum(h_font.getbbox(l)[3] - h_font.getbbox(l)[1] for l in h_lines) + 12 * (len(h_lines) - 1)
        top = (H - block_h) // 2 - 60
        after = render.draw_centered_block(df, h_lines, h_font, text_on_accent, W // 2, top, line_gap=12)

        if body:
            b_font, b_lines = render.fit_text(render.load_regular, body, int(W * 0.78),
                                               max_size=36, min_size=20)
            render.draw_centered_block(df, b_lines, b_font, text_on_accent, W // 2, after + 30, line_gap=8)

        if brand:
            bf = render.load_regular(24)
            bbox = bf.getbbox(brand)
            df.text(((W - (bbox[2] - bbox[0])) // 2, H - 80), brand, font=bf, fill=text_on_accent)
        images.append(img_final)

    return images


def write_caption(path: Path, caption: str, hashtags: list) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tags = " ".join(hashtags)
    body = [
        "=== Instagram Caption ===",
        "",
        caption.strip(),
        "",
        "---",
        "Hashtags (paste these as the first comment, or at end of caption):",
        tags,
    ]
    path.write_text("\n".join(body))
    return path
