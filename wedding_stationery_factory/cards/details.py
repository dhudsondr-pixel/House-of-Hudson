"""Details / Info card — 5x3.5" landscape with venue, hotels, transport."""

from ..pdf_engine import INCH, Card, SIZES


def build(canvas, theme, mode: str = "fillable") -> None:
    card = Card(canvas, theme, SIZES["5x3.5"], mode=mode)
    w, h = card.w, card.h

    card.small_caps("The Details", h - 0.50 * INCH, size=10, tracking=4)
    card.hairline(h - 0.72 * INCH, width_pt=60)

    sections = [
        ("CEREMONY",       "ceremony_info",  "5:00 PM at Trinity Chapel"),
        ("RECEPTION",      "reception_info", "6:30 PM at The Palmer House"),
        ("ACCOMMODATIONS", "hotel_info",     "Hampton Inn, code WED2026"),
        ("TRANSPORTATION", "transport_info", "Shuttle from hotel at 4:30 PM"),
    ]

    label_x = 0.45 * INCH
    field_x = 1.55 * INCH
    field_w = w - field_x - 0.30 * INCH
    y0 = h - 1.10 * INCH
    row_h = 0.45 * INCH

    for i, (label, field, example) in enumerate(sections):
        y = y0 - i * row_h
        card.small_caps(label, y, size=7, tracking=2,
                        x=label_x, align="left")
        card.textfield(field, field_x, y - 6, field_w, 0.34 * INCH,
                       font_size=9, font_name=theme.body_font,
                       placeholder=example)

    card.end_page()
