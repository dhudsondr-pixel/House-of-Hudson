"""Monthly habit tracker grid (31 days x N habits)."""

from ..pdf_engine import MARGIN, PAGE_W, Page


def build(canvas, theme) -> None:
    p = Page(canvas, theme)
    y = p.title("HABIT TRACKER")
    y = p.subtitle("MONTH ____________   YEAR ______", y)

    days = 31
    habits = 16
    grid_left = MARGIN + 130
    grid_top = y - 12
    cell_w = (PAGE_W - MARGIN - grid_left) / days
    cell_h = 30  # taller cells so the grid fills more of the page

    # Day number header
    for d in range(days):
        p.label(str(d + 1), grid_left + d * cell_w + cell_w / 2 - 3,
                grid_top + 2, size=7)

    # Habit row label lines (one underline per habit, aligned to grid cells)
    p.label("HABIT", MARGIN, grid_top + 2, size=8)
    for r in range(habits):
        yy = grid_top - (r + 1) * cell_h
        p.hline(MARGIN, yy, MARGIN + 125, weight=0.3)
    p.grid(grid_left, grid_top, days, habits, cell_w, cell_h)

    # Bottom: reflection (sits just under the grid; grid now fills the page)
    bottom_y = grid_top - habits * cell_h - 24
    p.label("REFLECTION", MARGIN, bottom_y, size=10)
    p.lined_area(MARGIN, bottom_y - 4, PAGE_W - 2 * MARGIN,
                 rows=2, row_h=16)

    p.footer("habit tracker  ·  31 day grid  ·  US Letter")
    canvas.showPage()
