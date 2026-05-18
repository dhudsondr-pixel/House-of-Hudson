"""Thank You card — 5x3.5" landscape, sent after the wedding."""

from ..pdf_engine import INCH, Card, SIZES


def build(canvas, theme, mode: str = "fillable") -> None:
    card = Card(canvas, theme, SIZES["5x3.5"], mode=mode)
    w, h = card.w, card.h

    card.c.setFillColorRGB(*theme.primary)
    card.c.setFont(theme.title_font, 36)
    card.c.drawCentredString(w / 2, h - 1.55 * INCH, "thank you")

    card.hairline(h - 1.85 * INCH, width_pt=80)

    card.small_caps("With love and gratitude", h - 2.10 * INCH,
                    size=8, tracking=3)
    card.textfield("couple_signature", 1.0 * INCH, h - 2.60 * INCH,
                   w - 2.0 * INCH, 0.30 * INCH,
                   font_size=14, font_name=theme.title_font,
                   placeholder="Anna & John")

    card.textfield("wedding_date", 1.3 * INCH, h - 3.00 * INCH,
                   w - 2.6 * INCH, 0.22 * INCH,
                   font_size=9, font_name=theme.body_font,
                   placeholder="August 12, 2026")

    card.end_page()
