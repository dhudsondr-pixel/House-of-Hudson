"""Render a customer-facing quote PDF for a custom print job."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from reportlab.lib.colors import Color, black
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def build_quote_pdf(
    out_path: Path,
    business_name: str,
    business_tagline: str,
    business_contact: str,
    customer_name: str,
    job_name: str,
    job_description: str,
    bbox_mm: tuple[float, float, float],
    print_time_hours: float,
    filament_weight_g: float,
    material: str,
    quote_total: float,
    breakdown: str,
    currency: str = "$",
    valid_days: int = 14,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=LETTER)
    W, H = LETTER

    # ---- Header ----
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(black)
    c.drawString(0.7 * inch, H - 0.9 * inch, business_name)

    if business_tagline:
        c.setFont("Helvetica-Oblique", 11)
        c.setFillColor(Color(0.4, 0.4, 0.4))
        c.drawString(0.7 * inch, H - 1.15 * inch, business_tagline)

    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    c.drawString(0.7 * inch, H - 1.35 * inch, business_contact)

    # Quote label / date.
    c.setFont("Helvetica-Bold", 28)
    c.drawRightString(W - 0.7 * inch, H - 0.9 * inch, "QUOTE")
    today = dt.date.today()
    valid_until = today + dt.timedelta(days=valid_days)
    c.setFont("Helvetica", 10)
    c.drawRightString(W - 0.7 * inch, H - 1.15 * inch, f"Date: {today.isoformat()}")
    c.drawRightString(W - 0.7 * inch, H - 1.30 * inch, f"Valid until: {valid_until.isoformat()}")

    # Divider.
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.line(0.7 * inch, H - 1.6 * inch, W - 0.7 * inch, H - 1.6 * inch)

    # ---- Customer ----
    y = H - 2.0 * inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.7 * inch, y, "PREPARED FOR")
    c.setFont("Helvetica", 12)
    c.drawString(0.7 * inch, y - 18, customer_name or "Customer")

    # ---- Job ----
    y -= 60
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.7 * inch, y, "PROJECT")
    c.setFont("Helvetica", 12)
    c.drawString(0.7 * inch, y - 18, job_name)

    # Description (wrapped).
    if job_description:
        c.setFont("Helvetica", 10)
        import textwrap
        wrapped = textwrap.wrap(job_description, width=80)
        dy = y - 40
        for line in wrapped[:6]:
            c.drawString(0.7 * inch, dy, line)
            dy -= 14
        y = dy
    else:
        y -= 40

    # ---- Specs table ----
    y -= 30
    c.setStrokeColor(Color(0.85, 0.85, 0.85))
    c.setFillColor(Color(0.97, 0.97, 0.97))
    table_top = y
    c.rect(0.7 * inch, y - 110, W - 1.4 * inch, 110, fill=1, stroke=1)
    c.setFillColor(black)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.9 * inch, y - 18, "Print specifications")

    c.setFont("Helvetica", 10)
    w, d, h = bbox_mm
    rows = [
        ("Dimensions", f"{w:.0f} × {d:.0f} × {h:.0f} mm"),
        ("Material", material),
        ("Estimated filament", f"{filament_weight_g:.0f} g"),
        ("Estimated print time", f"{print_time_hours:.1f} hours"),
    ]
    row_y = y - 38
    for label, value in rows:
        c.drawString(0.9 * inch, row_y, label)
        c.drawString(3.2 * inch, row_y, value)
        row_y -= 16

    y = y - 110 - 30

    # ---- Pricing breakdown ----
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.7 * inch, y, "PRICING")
    y -= 18
    c.setFont("Helvetica", 9)
    c.setFillColor(Color(0.35, 0.35, 0.35))
    for line in breakdown.splitlines():
        c.drawString(0.7 * inch, y, line)
        y -= 12

    # ---- Total ----
    y -= 14
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.line(0.7 * inch, y, W - 0.7 * inch, y)
    y -= 24

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.7 * inch, y, "Total")
    c.drawRightString(W - 0.7 * inch, y, f"{currency}{quote_total:.2f}")

    # ---- Terms / footer ----
    y -= 50
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(Color(0.45, 0.45, 0.45))
    terms = (
        "Quote includes filament, machine time, labor, and finishing. "
        "Shipping not included unless noted. 50% deposit due before print starts. "
        "Print times are estimates; final time depends on the slicer settings agreed at order."
    )
    import textwrap
    for line in textwrap.wrap(terms, width=100):
        c.drawString(0.7 * inch, y, line)
        y -= 12

    # Signature line.
    y -= 30
    c.setStrokeColor(black)
    c.line(0.7 * inch, y, 3.5 * inch, y)
    c.line(W - 3.5 * inch, y, W - 0.7 * inch, y)
    c.setFont("Helvetica", 9)
    c.setFillColor(Color(0.4, 0.4, 0.4))
    c.drawString(0.7 * inch, y - 14, "Customer signature")
    c.drawRightString(W - 0.7 * inch, y - 14, business_name)

    c.showPage()
    c.save()
    return out_path
