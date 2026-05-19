"""Wedding-style Etsy mockup images.

Three images per listing — all 2000x2000:
  1. Hero — large title with theme name, brand-photo feel.
  2. Card-on-background — shows the actual card centered on a tinted ground.
  3. Editable feature card — bullet list of "what's editable / what's included".
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import pypdfium2 as pdfium

from .themes import WeddingTheme


CANVAS = 2000


def _rgb255(c):
    return tuple(int(round(v * 255)) for v in c)


def _font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.ImageFont:
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/Library/Fonts/Georgia Bold.ttf",
        "C:\\Windows\\Fonts\\georgiab.ttf",
    ]
    candidates_italic = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        "/Library/Fonts/Georgia Italic.ttf",
        "C:\\Windows\\Fonts\\georgiai.ttf",
    ]
    candidates_reg = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/Library/Fonts/Georgia.ttf",
        "C:\\Windows\\Fonts\\georgia.ttf",
    ]
    candidates_sans = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Helvetica.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]
    pool = candidates_italic if italic else (candidates_bold if bold else candidates_reg)
    for c in pool + candidates_sans:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default(size=size)


def _draw_centered(d, box, text, font, fill):
    x0, y0, x1, y1 = box
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((x0 + (x1 - x0 - tw) / 2, y0 + (y1 - y0 - th) / 2),
           text, font=font, fill=fill)


def hero(theme: WeddingTheme, card_display_name: str, out_path: str) -> None:
    img = Image.new("RGB", (CANVAS, CANVAS), _rgb255(theme.background))
    d = ImageDraw.Draw(img)

    # Top: thin double line frame
    inset = 120
    d.rectangle([inset, inset, CANVAS - inset, CANVAS - inset],
                outline=_rgb255(theme.accent), width=4)
    d.rectangle([inset + 16, inset + 16, CANVAS - inset - 16,
                 CANVAS - inset - 16],
                outline=_rgb255(theme.accent), width=2)

    # Top small caps label
    _draw_centered(d, (0, 320, CANVAS, 420),
                   "EDITABLE  ·  PRINTABLE",
                   _font(54, bold=False),
                   _rgb255(theme.accent))

    # Big card name (italic serif)
    _draw_centered(d, (200, 600, CANVAS - 200, 1000),
                   card_display_name,
                   _font(180, italic=True),
                   _rgb255(theme.primary))

    # Hairline
    d.line([CANVAS / 2 - 200, 1080, CANVAS / 2 + 200, 1080],
           fill=_rgb255(theme.accent), width=3)

    # Theme name
    _draw_centered(d, (0, 1200, CANVAS, 1320),
                   theme.display_name.upper(),
                   _font(58, bold=True),
                   _rgb255(theme.text))

    # Bottom tagline
    _draw_centered(d, (0, 1600, CANVAS, 1700),
                   "instant download  ·  edit in adobe reader  ·  print at home",
                   _font(38, italic=True),
                   _rgb255(theme.accent))

    img.save(out_path, "PNG", optimize=True)


def card_on_background(theme: WeddingTheme, card_pdf_path: str,
                       out_path: str) -> None:
    """Render the actual card PDF into an image, centered on a tinted background."""
    bg_color = _rgb255(theme.accent)
    img = Image.new("RGB", (CANVAS, CANVAS), bg_color)

    # Render the PDF's first page. Close the document before returning so
    # Windows releases the file handle and the caller can delete the preview.
    pdf = pdfium.PdfDocument(card_pdf_path)
    try:
        page = pdf[0]
        # scale so that the longer side is ~1400px
        target = 1400
        pdf_w, pdf_h = page.get_size()
        scale = target / max(pdf_w, pdf_h)
        bitmap = page.render(scale=scale)
        card_img = bitmap.to_pil().convert("RGB")
        cw, ch = card_img.size
    finally:
        pdf.close()

    # Drop shadow
    shadow = Image.new("RGB", (cw + 40, ch + 40),
                       tuple(max(0, c - 30) for c in bg_color))
    sx = (CANVAS - shadow.size[0]) // 2
    sy = (CANVAS - shadow.size[1]) // 2
    img.paste(shadow, (sx, sy))

    # Paste card
    x = (CANVAS - cw) // 2
    y = (CANVAS - ch) // 2
    img.paste(card_img, (x, y))

    img.save(out_path, "PNG", optimize=True)


def feature_card(theme: WeddingTheme, card_display_name: str,
                 out_path: str) -> None:
    img = Image.new("RGB", (CANVAS, CANVAS), _rgb255(theme.background))
    d = ImageDraw.Draw(img)

    _draw_centered(d, (0, 200, CANVAS, 320),
                   "WHAT YOU CAN EDIT",
                   _font(54, bold=True),
                   _rgb255(theme.accent))
    _draw_centered(d, (0, 360, CANVAS, 540),
                   card_display_name.upper(),
                   _font(120, italic=True),
                   _rgb255(theme.primary))

    d.line([CANVAS / 2 - 180, 620, CANVAS / 2 + 180, 620],
           fill=_rgb255(theme.accent), width=3)

    bullets = [
        "Couple names + monogram",
        "Wedding date + time",
        "Venue + ceremony location",
        "Reception details",
        "Custom message lines",
        "Print as many copies as you need",
    ]
    body_f = _font(54, bold=False)
    y = 820
    for b in bullets:
        # Dot
        d.ellipse([320, y + 18, 360, y + 58], fill=_rgb255(theme.accent))
        d.text((420, y), b, font=body_f, fill=_rgb255(theme.text))
        y += 130

    img.save(out_path, "PNG", optimize=True)
