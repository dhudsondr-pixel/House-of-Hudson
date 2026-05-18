"""RSVP card — 5x3.5" landscape. Single-column layout to avoid crowding."""

from ..pdf_engine import INCH, Card, SIZES


def build(canvas, theme, mode: str = "fillable") -> None:
    card = Card(canvas, theme, SIZES["5x3.5"], mode=mode)
    w, h = card.w, card.h

    card.small_caps("Kindly Reply By", h - 0.45 * INCH, size=8, tracking=3)

    card.textfield("reply_by_date", 1.25 * INCH, h - 0.85 * INCH,
                   w - 2.5 * INCH, 0.28 * INCH,
                   font_size=14, font_name=theme.title_font,
                   placeholder="July 1, 2026")

    card.hairline(h - 1.10 * INCH, width_pt=50)

    # "M ____" full-width guest name row.
    card.c.setFillColorRGB(*theme.text)
    card.c.setFont(theme.body_font, 11)
    card.c.drawString(0.45 * INCH, h - 1.55 * INCH, "M")
    card.textfield("guest_name", 0.65 * INCH, h - 1.65 * INCH,
                   w - 1.10 * INCH, 0.24 * INCH,
                   font_size=11, font_name=theme.body_font,
                   placeholder="r. and Mrs. Robert Smith")

    # Accepts / declines checkboxes — left column
    box_y = h - 2.10 * INCH
    card.c.setStrokeColorRGB(*theme.muted)
    card.c.setLineWidth(0.5)
    card.c.rect(0.55 * INCH, box_y, 10, 10, stroke=1, fill=0)
    card.c.setFillColorRGB(*theme.text)
    card.c.setFont(theme.small_font, 10)
    card.c.drawString(0.55 * INCH + 16, box_y + 1, "Joyfully accepts")
    card.c.rect(0.55 * INCH, box_y - 22, 10, 10, stroke=1, fill=0)
    card.c.drawString(0.55 * INCH + 16, box_y - 21, "Regretfully declines")

    # # of guests + entree on a separate line, full width.
    detail_y = box_y - 50
    card.c.setFont(theme.body_font, 10)
    card.c.drawString(0.55 * INCH, detail_y, "# Attending:")
    card.textfield("guests_count", 1.55 * INCH, detail_y - 3,
                   0.45 * INCH, 0.22 * INCH,
                   font_size=10, font_name=theme.body_font,
                   placeholder="2")
    card.c.drawString(2.30 * INCH, detail_y, "Meal:")
    card.textfield("entree", 2.75 * INCH, detail_y - 3,
                   w - 2.75 * INCH - 0.40 * INCH, 0.22 * INCH,
                   font_size=10, font_name=theme.body_font,
                   placeholder="Beef / Salmon / Veg")

    card.end_page()
