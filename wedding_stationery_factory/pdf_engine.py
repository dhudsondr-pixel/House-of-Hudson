"""Wedding-specific PDF helpers.

Differences from the planner engine:
- Variable page sizes (cards are not US Letter; they're 5x7, 5x3.5, etc.).
- Decorative motifs (frames, flourishes, monograms).
- AcroForm text fields so buyers can fill in their names/date/venue in
  free Adobe Reader without needing Canva/Corjl.
"""

from dataclasses import dataclass

from reportlab.pdfgen import canvas as pdfcanvas

from .themes import WeddingTheme


INCH = 72.0


@dataclass(frozen=True)
class CardSize:
    name: str
    width_in: float
    height_in: float

    @property
    def pts(self) -> tuple[float, float]:
        return (self.width_in * INCH, self.height_in * INCH)


SIZES = {
    "5x7": CardSize("5x7", 5.0, 7.0),
    "7x5": CardSize("7x5", 7.0, 5.0),
    "5x3.5": CardSize("5x3.5", 5.0, 3.5),
    "4x9": CardSize("4x9", 4.0, 9.0),
    "4x6": CardSize("4x6", 4.0, 6.0),
}


class Card:
    """One side of one wedding card. Wraps a reportlab canvas with helpers.

    ``mode='fillable'`` (default) — the file the customer downloads.
    Text fields are real AcroForm fields with NO default value; placeholders
    are ignored.

    ``mode='preview'`` — used internally to generate the listing mockup image.
    Placeholders are drawn as static text so the preview shows what a
    filled-in card looks like. Never given to the customer.
    """

    def __init__(self, c: pdfcanvas.Canvas, theme: WeddingTheme,
                 size: CardSize, mode: str = "fillable"):
        if mode not in ("fillable", "preview"):
            raise ValueError(f"unknown mode: {mode}")
        self.c = c
        self.theme = theme
        self.size = size
        self.mode = mode
        self.w, self.h = size.pts
        c.setPageSize((self.w, self.h))
        # Background
        c.setFillColorRGB(*theme.background)
        c.rect(0, 0, self.w, self.h, stroke=0, fill=1)
        # Theme-specific decorative motif
        self._draw_motif()

    # -------- decorative motifs --------

    def _draw_motif(self) -> None:
        # On small cards (< 4" tall) the motif crowds the type — skip the
        # heavier decorations (monogram ring, flourish) but keep frames.
        small_card = self.h < 4 * INCH
        m = self.theme.motif
        if m == "frame":
            self._frame_border()
        elif m == "flourish" and not small_card:
            self._flourish_dividers()
        elif m == "monogram" and not small_card:
            self._monogram_ring()
        # 'minimal' draws nothing

    def _frame_border(self) -> None:
        inset = 0.25 * INCH
        self.c.setStrokeColorRGB(*self.theme.accent)
        self.c.setLineWidth(0.6)
        self.c.rect(inset, inset, self.w - 2 * inset, self.h - 2 * inset,
                    stroke=1, fill=0)
        # double-line elegance: tiny inner frame
        inset2 = inset + 4
        self.c.setLineWidth(0.3)
        self.c.rect(inset2, inset2, self.w - 2 * inset2, self.h - 2 * inset2,
                    stroke=1, fill=0)

    def _flourish_dividers(self) -> None:
        # subtle leaf-like marks in two corners
        self.c.setStrokeColorRGB(*self.theme.accent)
        self.c.setFillColorRGB(*self.theme.accent)
        self.c.setLineWidth(0.5)
        # top-center small flourish (a horizontal line with a leaf tip)
        cx = self.w / 2
        top_y = self.h - 0.45 * INCH
        self.c.line(cx - 24, top_y, cx + 24, top_y)
        # tiny leaves (filled ellipses)
        self.c.ellipse(cx - 28, top_y - 2, cx - 22, top_y + 2, stroke=0, fill=1)
        self.c.ellipse(cx + 22, top_y - 2, cx + 28, top_y + 2, stroke=0, fill=1)

    def _monogram_ring(self) -> None:
        # thin circle near the top center as a placeholder for a monogram
        cx = self.w / 2
        cy = self.h - 0.65 * INCH
        r = 18
        self.c.setStrokeColorRGB(*self.theme.accent)
        self.c.setLineWidth(0.6)
        self.c.circle(cx, cy, r, stroke=1, fill=0)

    # -------- text helpers --------

    def title(self, text: str, y: float, size: int = 32) -> None:
        self.c.setFillColorRGB(*self.theme.primary)
        self.c.setFont(self.theme.title_font, size)
        self.c.drawCentredString(self.w / 2, y, text)

    def small_caps(self, text: str, y: float, size: int = 8,
                   tracking: float = 2.0,
                   x: float | None = None,
                   align: str = "center") -> None:
        """Letter-spaced uppercase line, the wedding-stationery staple."""
        upper = text.upper()
        # Use a text object so we can set character spacing (Canvas lacks it).
        # Pre-measure the spaced width so we can center it.
        self.c.setFillColorRGB(*self.theme.accent)
        from reportlab.pdfbase.pdfmetrics import stringWidth
        base_w = stringWidth(upper, self.theme.small_font, size)
        spaced_w = base_w + tracking * max(0, len(upper) - 1)
        if align == "left" and x is not None:
            start_x = x
        else:
            start_x = (self.w - spaced_w) / 2

        to = self.c.beginText(start_x, y)
        to.setFont(self.theme.small_font, size)
        to.setCharSpace(tracking)
        to.textOut(upper)
        self.c.drawText(to)

    def body(self, text: str, y: float, size: int = 11) -> None:
        self.c.setFillColorRGB(*self.theme.text)
        self.c.setFont(self.theme.body_font, size)
        self.c.drawCentredString(self.w / 2, y, text)

    def hairline(self, y: float, width_pt: float = 60) -> None:
        self.c.setStrokeColorRGB(*self.theme.accent)
        self.c.setLineWidth(0.5)
        self.c.line(self.w / 2 - width_pt / 2, y,
                    self.w / 2 + width_pt / 2, y)

    # -------- form fields (fillable PDF) --------

    def textfield(self, name: str, x: float, y: float, w: float, h: float,
                  *, font_size: int = 11, centered: bool = True,
                  font_name: str | None = None,
                  placeholder: str = "") -> None:
        """Fillable text field — buyers type their details in Adobe Reader.

        In preview mode, the placeholder is rendered as static text so the
        listing image shows a card filled with example data.
        """
        font = font_name or self.theme.body_font

        if self.mode == "preview" and placeholder:
            # Bake the placeholder as visible static text, vertically centered.
            self.c.setFillColorRGB(*self.theme.text)
            self.c.setFont(font, font_size)
            text_y = y + (h - font_size) / 2 + 2
            text_x = x + w / 2 if centered else x + 4
            if centered:
                self.c.drawCentredString(text_x, text_y, _safe_text(placeholder))
            else:
                self.c.drawString(text_x, text_y, _safe_text(placeholder))
            return

        # Fillable mode — real AcroForm field with no default value.
        self.c.acroForm.textfield(
            name=name,
            tooltip=name,
            value="",
            x=x, y=y, width=w, height=h,
            fontName=font,
            fontSize=font_size,
            textColor=_pdfcolor(self.theme.text),
            fillColor=_pdfcolor(self.theme.background),
            borderColor=_pdfcolor(self.theme.muted, alpha=0),
            borderWidth=0,
            forceBorder=False,
            relative=False,
            fieldFlags="doNotScroll",
            maxlen=200,
        )
        # Subtle underline so buyers see where the field is when printed.
        self.c.setStrokeColorRGB(*self.theme.muted)
        self.c.setLineWidth(0.3)
        self.c.line(x + 4, y - 2, x + w - 4, y - 2)

    def end_page(self) -> None:
        self.c.showPage()


def _pdfcolor(rgb, alpha: float = 1.0):
    """Convert (r, g, b) floats in 0..1 to a reportlab Color."""
    from reportlab.lib.colors import Color
    return Color(rgb[0], rgb[1], rgb[2], alpha=alpha)


# Characters that reportlab's AcroForm escape table doesn't know how to handle.
_REPLACEMENTS = {
    "•": "-",   # bullet
    "–": "-",   # en dash
    "—": "-",   # em dash
    "‘": "'",   # left single quote
    "’": "'",   # right single quote
    "“": '"',   # left double quote
    "”": '"',   # right double quote
    "é": "e",   # é
    "è": "e",   # è
    "ê": "e",   # ê
    "à": "a",   # à
    "ñ": "n",   # ñ
    "ü": "u",   # ü
    "×": "x",   # ×
    " ": " ",   # nbsp
}


def _safe_text(s: str) -> str:
    """Strip characters that reportlab's form-field encoder can't handle."""
    if not s:
        return s
    for k, v in _REPLACEMENTS.items():
        if k in s:
            s = s.replace(k, v)
    # Final fallback: anything still non-Latin-1 gets dropped.
    return s.encode("latin-1", "ignore").decode("latin-1")


def new_card_doc(path: str) -> pdfcanvas.Canvas:
    c = pdfcanvas.Canvas(path, pagesize=(5 * INCH, 7 * INCH))
    c.setTitle("Wedding Stationery — Editable Template")
    return c
