"""Undated weekly planner spread."""

from ..pdf_engine import MARGIN, PAGE_H, PAGE_W, Page


def build(canvas, theme) -> None:
    p = Page(canvas, theme)
    y = p.title("WEEK AT A GLANCE")
    y = p.subtitle("WEEK OF ____________", y)

    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY",
            "FRIDAY", "SATURDAY", "SUNDAY"]
    row_h = 72  # generous; 7 days * 72 = 504pt of the ~640pt body
    cur = y - 6

    for d in days:
        p.label(d, MARGIN, cur - 2, size=10)
        p.hline(MARGIN + 80, cur - 1, PAGE_W - MARGIN, weight=0.6)
        # Four task lines per day
        for i in range(4):
            line_y = cur - 16 - i * 14
            p.checkbox(MARGIN + 82, line_y - 2, 8)
            p.hline(MARGIN + 96, line_y - 4, PAGE_W - MARGIN, weight=0.3)
        cur -= row_h

    # Goals + notes
    cur -= 4
    half = (PAGE_W - 2 * MARGIN - 16) / 2
    p.label("THIS WEEK'S GOALS", MARGIN, cur, size=10)
    p.label("NOTES", MARGIN + half + 16, cur, size=10)
    p.lined_area(MARGIN, cur - 4, half, rows=4, row_h=18)
    p.lined_area(MARGIN + half + 16, cur - 4, half, rows=4, row_h=18)

    p.footer("weekly planner  ·  undated  ·  US Letter")
    canvas.showPage()
