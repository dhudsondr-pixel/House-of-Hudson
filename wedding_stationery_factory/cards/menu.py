"""Wedding Menu — 4x9" tall menu card, place-setting style."""

from ..pdf_engine import INCH, Card, SIZES


def build(canvas, theme, mode: str = "fillable") -> None:
    card = Card(canvas, theme, SIZES["4x9"], mode=mode)
    w, h = card.w, card.h

    card.small_caps("Menu", h - 0.85 * INCH, size=14, tracking=6)
    card.hairline(h - 1.15 * INCH, width_pt=60)

    courses = [
        ("First Course", "first_course",
         "Heirloom tomato salad",
         "burrata, basil oil"),
        ("Salad", "salad_course",
         "Roasted beet",
         "goat cheese, walnut"),
        ("Main Course", "main_course",
         "Filet of beef",
         "potato puree, red wine jus"),
        ("Dessert", "dessert_course",
         "Lemon mascarpone tart",
         "raspberry coulis"),
    ]

    y = h - 1.80 * INCH
    course_block = 1.55 * INCH

    for course_label, field_name, ex_name, ex_desc in courses:
        card.small_caps(course_label, y, size=9, tracking=3)
        card.textfield(f"{field_name}_name", 0.30 * INCH, y - 0.40 * INCH,
                       w - 0.60 * INCH, 0.28 * INCH,
                       font_size=12, font_name=theme.title_font,
                       placeholder=ex_name)
        card.textfield(f"{field_name}_desc", 0.30 * INCH, y - 0.78 * INCH,
                       w - 0.60 * INCH, 0.26 * INCH,
                       font_size=9, font_name=theme.body_font,
                       placeholder=ex_desc)
        card.hairline(y - 1.10 * INCH, width_pt=30)
        y -= course_block

    card.end_page()
