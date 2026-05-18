"""Goal setting workbook page (SMART goals + action steps)."""

from ..pdf_engine import MARGIN, PAGE_W, Page


def build(canvas, theme) -> None:
    p = Page(canvas, theme)
    y = p.title("GOAL SETTING")
    y = p.subtitle("THE GOAL THAT MATTERS MOST RIGHT NOW", y)

    # Main goal box
    p.box(MARGIN, y - 70, PAGE_W - 2 * MARGIN, 60)
    p.label("MY GOAL", MARGIN + 8, y - 22, size=9)
    y -= 90

    # SMART rows
    smart = [
        ("SPECIFIC",   "What exactly will I accomplish?"),
        ("MEASURABLE", "How will I know when I'm done?"),
        ("ACHIEVABLE", "Why is this realistic for me?"),
        ("RELEVANT",   "Why does this matter?"),
        ("TIME-BOUND", "Deadline:"),
    ]
    for label, prompt in smart:
        p.label(label, MARGIN, y, size=10)
        p.label(prompt, MARGIN + 90, y, size=9)
        p.hline(MARGIN, y - 16, PAGE_W - MARGIN, weight=0.4)
        p.hline(MARGIN, y - 32, PAGE_W - MARGIN, weight=0.4)
        y -= 46

    # Action steps
    p.label("ACTION STEPS", MARGIN, y, size=10)
    for i in range(5):
        yy = y - 14 - i * 16
        p.checkbox(MARGIN, yy - 2, 9)
        p.hline(MARGIN + 14, yy - 4, PAGE_W - MARGIN, weight=0.4)

    p.footer("goal setting workbook  ·  US Letter")
    canvas.showPage()
