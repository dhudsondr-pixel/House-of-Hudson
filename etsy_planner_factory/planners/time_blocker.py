"""Hourly time-blocking template (5am-11pm in 30-min slots)."""

from ..pdf_engine import MARGIN, PAGE_W, Page


def build(canvas, theme) -> None:
    p = Page(canvas, theme)
    y = p.title("TIME BLOCK")
    y = p.subtitle("DATE __________   DEEP WORK FOCUS: __________", y)

    # Two columns of half-hour slots, 5:00am to 11:00pm = 36 slots
    slots = []
    for h in range(5, 23):
        for m in (0, 30):
            slots.append(f"{((h - 1) % 12) + 1:>2}:{m:02d} {'AM' if h < 12 else 'PM'}")
    # 36 slots total. 18 per column.
    half = (PAGE_W - 2 * MARGIN - 20) / 2
    col_top = y - 8
    row_h = 19

    for i, label in enumerate(slots):
        col = i // 18
        row = i % 18
        x = MARGIN + col * (half + 20)
        yy = col_top - row * row_h
        p.label(label, x, yy - 8, size=8)
        p.hline(x + 44, yy - 10, x + half, weight=0.4)

    # Bottom: priorities + reflection
    bottom_y = col_top - 18 * row_h - 14
    p.label("PRIORITIES", MARGIN, bottom_y, size=10)
    for i in range(3):
        yy = bottom_y - 14 - i * 14
        p.checkbox(MARGIN, yy - 2, 9)
        p.hline(MARGIN + 14, yy - 4, MARGIN + half, weight=0.4)

    p.label("REFLECTION", MARGIN + half + 20, bottom_y, size=10)
    p.lined_area(MARGIN + half + 20, bottom_y - 4, half, rows=3, row_h=14)

    p.footer("time blocking planner  ·  US Letter")
    canvas.showPage()
