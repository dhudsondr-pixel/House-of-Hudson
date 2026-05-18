"""Thin reportlab wrapper to keep planner code declarative."""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdfcanvas

from .themes import Theme


PAGE_W, PAGE_H = letter  # 612 x 792 pts (US Letter)
MARGIN = 50.0


class Page:
    def __init__(self, c: pdfcanvas.Canvas, theme: Theme):
        self.c = c
        self.theme = theme
        # Fill background
        c.setFillColorRGB(*theme.background)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    def title(self, text: str, y: float | None = None) -> float:
        y = y if y is not None else PAGE_H - MARGIN - 10
        self.c.setFillColorRGB(*self.theme.primary)
        self.c.setFont(self.theme.header_font, 28)
        self.c.drawString(MARGIN, y, text)
        # Accent underline
        self.c.setStrokeColorRGB(*self.theme.primary)
        self.c.setLineWidth(2)
        self.c.line(MARGIN, y - 8, MARGIN + 60, y - 8)
        return y - 30

    def subtitle(self, text: str, y: float) -> float:
        self.c.setFillColorRGB(*self.theme.secondary)
        self.c.setFont(self.theme.body_font, 11)
        self.c.drawString(MARGIN, y, text)
        return y - 22

    def label(self, text: str, x: float, y: float, size: int = 9) -> None:
        self.c.setFillColorRGB(*self.theme.secondary)
        self.c.setFont(self.theme.body_font, size)
        self.c.drawString(x, y, text)

    def hline(self, x1: float, y: float, x2: float, weight: float = 0.5) -> None:
        self.c.setStrokeColorRGB(*self.theme.muted)
        self.c.setLineWidth(weight)
        self.c.line(x1, y, x2, y)

    def vline(self, x: float, y1: float, y2: float, weight: float = 0.5) -> None:
        self.c.setStrokeColorRGB(*self.theme.muted)
        self.c.setLineWidth(weight)
        self.c.line(x, y1, x, y2)

    def box(self, x: float, y: float, w: float, h: float, weight: float = 0.5) -> None:
        self.c.setStrokeColorRGB(*self.theme.muted)
        self.c.setLineWidth(weight)
        self.c.rect(x, y, w, h, stroke=1, fill=0)

    def filled_box(self, x: float, y: float, w: float, h: float, color: tuple) -> None:
        self.c.setFillColorRGB(*color)
        self.c.rect(x, y, w, h, stroke=0, fill=1)

    def checkbox(self, x: float, y: float, size: float = 9.0) -> None:
        self.box(x, y, size, size, weight=0.7)

    def lined_area(self, x: float, y_top: float, w: float, rows: int,
                   row_h: float = 22) -> float:
        for i in range(rows):
            yy = y_top - row_h * (i + 1)
            self.hline(x, yy, x + w, weight=0.4)
        return y_top - row_h * rows

    def grid(self, x: float, y_top: float, cols: int, rows: int,
             cell_w: float, cell_h: float) -> None:
        for r in range(rows + 1):
            self.hline(x, y_top - r * cell_h, x + cell_w * cols)
        for col in range(cols + 1):
            self.vline(x + col * cell_w, y_top - rows * cell_h, y_top)

    def footer(self, text: str = "") -> None:
        self.c.setFillColorRGB(*self.theme.muted)
        self.c.setFont(self.theme.body_font, 8)
        self.c.drawCentredString(PAGE_W / 2, 25, text)


def new_doc(path: str) -> pdfcanvas.Canvas:
    c = pdfcanvas.Canvas(path, pagesize=letter)
    c.setTitle("Printable Planner")
    return c
