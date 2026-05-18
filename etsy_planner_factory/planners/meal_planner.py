"""Weekly meal planner + grocery list combo page."""

from ..pdf_engine import MARGIN, PAGE_W, Page


def build(canvas, theme) -> None:
    p = Page(canvas, theme)
    y = p.title("MEAL PLAN")
    y = p.subtitle("WEEK OF ____________", y)

    # Days x meals grid
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    meals = ["BREAKFAST", "LUNCH", "DINNER"]

    label_w = 50
    col_w = (PAGE_W - 2 * MARGIN - label_w - 130) / 3  # 3 meal columns
    row_h = 62  # taller so the seven days fill the page
    top = y - 14

    # Column headers
    for ci, m in enumerate(meals):
        p.label(m, MARGIN + label_w + ci * col_w + 4, top + 6, size=9)

    for ri, d in enumerate(days):
        yy = top - (ri + 1) * row_h
        p.label(d, MARGIN, yy + row_h / 2 - 4, size=10)
        for ci in range(3):
            x = MARGIN + label_w + ci * col_w
            p.box(x, yy, col_w - 4, row_h - 4)

    # Grocery list (right side, full height)
    gx = MARGIN + label_w + 3 * col_w + 10
    gw = PAGE_W - MARGIN - gx
    p.label("GROCERY LIST", gx, top + 6, size=10)
    rows = int((row_h * 7) / 20)
    for i in range(rows):
        yy = top - 12 - i * 20
        p.checkbox(gx, yy - 2, 9)
        p.hline(gx + 14, yy - 4, gx + gw, weight=0.3)

    # Bottom: notes
    bottom_y = top - 7 * row_h - 24
    p.label("NOTES & PREP", MARGIN, bottom_y, size=10)
    p.lined_area(MARGIN, bottom_y - 4, PAGE_W - 2 * MARGIN, rows=4, row_h=20)

    p.footer("weekly meal planner  ·  US Letter")
    canvas.showPage()
