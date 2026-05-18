"""Undated daily planner page."""

from ..pdf_engine import MARGIN, PAGE_H, PAGE_W, Page


def build(canvas, theme) -> None:
    p = Page(canvas, theme)
    y = p.title("DAILY PLAN")
    y = p.subtitle("DATE  M  T  W  T  F  S  S", y)

    # Top stats row: top 3 priorities | water | mood
    box_top = y - 10
    box_h = 70

    # Priorities (left half)
    half = (PAGE_W - 2 * MARGIN) / 2 - 8
    p.label("TODAY'S TOP 3", MARGIN, box_top - 4, size=9)
    for i in range(3):
        yy = box_top - 18 - i * 16
        p.checkbox(MARGIN, yy, 9)
        p.hline(MARGIN + 16, yy - 2, MARGIN + half, weight=0.4)

    # Right column: water + mood
    rx = MARGIN + half + 16
    p.label("WATER", rx, box_top - 4, size=9)
    for i in range(8):
        p.checkbox(rx + i * 16, box_top - 22, 10)
    p.label("MOOD", rx, box_top - 42, size=9)
    moods = ["AWFUL", "MEH", "OK", "GOOD", "GREAT"]
    for i, m in enumerate(moods):
        p.checkbox(rx + i * 36, box_top - 56, 9)
        p.label(m, rx + i * 36 + 12, box_top - 54, size=7)

    y = box_top - box_h - 10

    # Schedule (left) + Tasks (right)
    col_w = (PAGE_W - 2 * MARGIN - 16) / 2
    p.label("SCHEDULE", MARGIN, y, size=10)
    p.label("TASKS", MARGIN + col_w + 16, y, size=10)
    y -= 12

    # Schedule: hours 6am - 9pm
    hours = ["6", "7", "8", "9", "10", "11", "12", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    row_h = 22
    for i, h in enumerate(hours):
        yy = y - row_h * (i + 1) + 6
        p.label(h, MARGIN, yy, size=9)
        p.hline(MARGIN + 16, yy - 4, MARGIN + col_w, weight=0.4)

    # Tasks: checkboxes
    tx = MARGIN + col_w + 16
    for i in range(16):
        yy = y - row_h * (i + 1) + 6
        p.checkbox(tx, yy - 1, 9)
        p.hline(tx + 14, yy - 4, tx + col_w, weight=0.4)

    # Bottom: notes
    notes_y = y - row_h * 16 - 14
    p.label("NOTES", MARGIN, notes_y, size=10)
    p.lined_area(MARGIN, notes_y - 4, PAGE_W - 2 * MARGIN, rows=3, row_h=18)

    p.footer("daily planner  ·  undated  ·  US Letter")
    canvas.showPage()
