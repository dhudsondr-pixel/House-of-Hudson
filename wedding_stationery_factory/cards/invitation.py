"""Wedding Invitation — 5x7" portrait, the centerpiece of the suite."""

from ..pdf_engine import INCH, Card, SIZES


def build(canvas, theme, mode: str = "fillable") -> None:
    card = Card(canvas, theme, SIZES["5x7"], mode=mode)
    w, h = card.w, card.h

    card.small_caps("Together with their families", h - 1.10 * INCH,
                    size=8, tracking=2.5)

    card.textfield("name_one", 0.6 * INCH, h - 2.10 * INCH,
                   w - 1.2 * INCH, 0.42 * INCH,
                   font_size=26, font_name=theme.title_font,
                   placeholder="Anna Margaret Smith")
    card.c.setFillColorRGB(*theme.accent)
    card.c.setFont(theme.title_font, 22)
    card.c.drawCentredString(w / 2, h - 2.50 * INCH, "&")
    card.textfield("name_two", 0.6 * INCH, h - 3.05 * INCH,
                   w - 1.2 * INCH, 0.42 * INCH,
                   font_size=26, font_name=theme.title_font,
                   placeholder="John Henry Davis")

    card.small_caps("Request the honor of your presence at their wedding",
                    h - 3.55 * INCH, size=7, tracking=2)

    card.hairline(h - 3.85 * INCH, width_pt=70)

    card.textfield("date", 0.5 * INCH, h - 4.45 * INCH,
                   w - 1.0 * INCH, 0.32 * INCH,
                   font_size=15, font_name=theme.body_font,
                   placeholder="Saturday, August 12, 2026")
    card.textfield("time", 0.5 * INCH, h - 4.95 * INCH,
                   w - 1.0 * INCH, 0.28 * INCH,
                   font_size=12, font_name=theme.body_font,
                   placeholder="Five o'clock in the evening")
    card.textfield("venue", 0.5 * INCH, h - 5.40 * INCH,
                   w - 1.0 * INCH, 0.28 * INCH,
                   font_size=12, font_name=theme.body_font,
                   placeholder="The Palmer House")
    card.textfield("venue_city", 0.5 * INCH, h - 5.78 * INCH,
                   w - 1.0 * INCH, 0.26 * INCH,
                   font_size=11, font_name=theme.body_font,
                   placeholder="Chicago, Illinois")

    card.hairline(h - 6.05 * INCH, width_pt=50)

    card.small_caps("Reception to follow", 0.55 * INCH, size=8, tracking=3)

    card.end_page()
