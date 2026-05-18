"""Save the Date — 7x5" landscape card with fillable name/date/location."""

from ..pdf_engine import INCH, Card, SIZES


def build(canvas, theme, mode: str = "fillable") -> None:
    card = Card(canvas, theme, SIZES["7x5"], mode=mode)
    w, h = card.w, card.h

    card.small_caps("Save the Date", h - 1.10 * INCH, size=10, tracking=4)

    card.textfield("couple_names", 0.7 * INCH, h - 2.30 * INCH,
                   w - 1.4 * INCH, 0.50 * INCH,
                   font_size=34, font_name=theme.title_font,
                   placeholder="Anna  &  John")

    card.hairline(h - 2.60 * INCH, width_pt=70)

    card.textfield("date", 1.0 * INCH, h - 3.30 * INCH,
                   w - 2.0 * INCH, 0.36 * INCH,
                   font_size=18, font_name=theme.body_font,
                   placeholder="August 12, 2026")

    card.textfield("location", 1.0 * INCH, h - 3.90 * INCH,
                   w - 2.0 * INCH, 0.30 * INCH,
                   font_size=12, font_name=theme.body_font,
                   placeholder="Chicago, Illinois")

    card.small_caps("Formal invitation to follow", 0.55 * INCH,
                    size=8, tracking=3)

    card.end_page()
