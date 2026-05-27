"""KDP interior PDF generators. Pure reportlab — no system font dependencies."""
from __future__ import annotations

import textwrap
from pathlib import Path
from typing import List

from reportlab.lib.colors import Color, black, grey
from reportlab.pdfgen import canvas

from .specs import (
    BOTTOM_MARGIN,
    INSIDE_MARGIN,
    OUTSIDE_MARGIN,
    TOP_MARGIN,
    TRIM_SIZES,
)


def _content_box(trim: str, page_num: int) -> tuple[float, float, float, float]:
    """Return (x0, y0, x1, y1) in points for the printable content area on this page."""
    tw, th = TRIM_SIZES[trim]
    is_right_page = page_num % 2 == 1  # 1, 3, 5, ... are right-hand pages
    if is_right_page:
        left = INSIDE_MARGIN
        right = OUTSIDE_MARGIN
    else:
        left = OUTSIDE_MARGIN
        right = INSIDE_MARGIN
    x0 = left * 72
    y0 = BOTTOM_MARGIN * 72
    x1 = (tw - right) * 72
    y1 = (th - TOP_MARGIN) * 72
    return x0, y0, x1, y1


def _draw_page_number(c: canvas.Canvas, trim: str, page_num: int) -> None:
    tw, th = TRIM_SIZES[trim]
    c.setFont("Helvetica", 9)
    c.setFillColor(grey)
    c.drawCentredString(tw * 72 / 2, 0.375 * 72, str(page_num))
    c.setFillColor(black)


def _wrap_to_width(c: canvas.Canvas, text: str, font: str, size: float, max_w: float) -> list[str]:
    """Wrap text so each line's RENDERED width fits within max_w points.

    Word-by-word using canvas.stringWidth (font-aware), unlike textwrap which
    counts characters. Returns the wrapped lines.
    """
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for w in words[1:]:
        trial = current + " " + w
        if c.stringWidth(trial, font, size) <= max_w:
            current = trial
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines


def _fit_font_size(c: canvas.Canvas, text: str, font: str, start_size: float,
                   max_w: float, min_size: float = 14) -> float:
    """Return a font size <= start_size such that the single longest sub-line
    (assuming text is split by whitespace into balanced lines) fits within max_w."""
    size = start_size
    while size >= min_size:
        # Try to wrap and see if every line fits.
        lines = _wrap_to_width(c, text, font, size, max_w)
        if all(c.stringWidth(line, font, size) <= max_w for line in lines):
            return size
        size -= 1
    return min_size


def _draw_title_page(c: canvas.Canvas, trim: str, title: str, subtitle: str, author: str) -> None:
    tw, th = TRIM_SIZES[trim]
    cx = tw * 72 / 2

    # Title page is page 1 (right-hand). Safe content width is the same as any
    # other right-hand page: trim - INSIDE_MARGIN - OUTSIDE_MARGIN. We use a
    # symmetric safe width (twice the smaller margin from center) so the
    # centered string can't poke into either margin.
    safe_w = (tw - 2 * max(INSIDE_MARGIN, OUTSIDE_MARGIN)) * 72

    c.setFillColor(black)
    title_size = _fit_font_size(c, title, "Helvetica-Bold", start_size=32,
                                max_w=safe_w, min_size=18)
    c.setFont("Helvetica-Bold", title_size)
    title_lines = _wrap_to_width(c, title, "Helvetica-Bold", title_size, safe_w)
    line_spacing = title_size * 1.18
    y = th * 72 * 0.6 + (len(title_lines) - 1) * line_spacing / 2
    for line in title_lines:
        c.drawCentredString(cx, y, line)
        y -= line_spacing

    if subtitle:
        sub_size = _fit_font_size(c, subtitle, "Helvetica", start_size=14,
                                  max_w=safe_w, min_size=10)
        c.setFont("Helvetica", sub_size)
        sub_lines = _wrap_to_width(c, subtitle, "Helvetica", sub_size, safe_w)
        y -= 10
        for line in sub_lines:
            c.drawCentredString(cx, y, line)
            y -= sub_size * 1.3

    if author:
        c.setFont("Helvetica-Oblique", 14)
        c.drawCentredString(cx, th * 72 * 0.25, author)


def _draw_belongs_to_page(c: canvas.Canvas, trim: str) -> None:
    tw, th = TRIM_SIZES[trim]
    cx = tw * 72 / 2
    cy = th * 72 / 2

    c.setFont("Helvetica", 16)
    c.setFillColor(black)
    c.drawCentredString(cx, cy + 40, "This journal belongs to:")
    # Underline for name.
    c.setStrokeColor(black)
    c.setLineWidth(0.8)
    c.line(cx - 130, cy - 4, cx + 130, cy - 4)


def _draw_lined_page(c: canvas.Canvas, trim: str, page_num: int, line_spacing_pt: float = 22) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    c.setStrokeColor(Color(0.78, 0.78, 0.78))
    c.setLineWidth(0.4)
    y = y1
    while y > y0:
        c.line(x0, y, x1, y)
        y -= line_spacing_pt


def _draw_dotted_page(c: canvas.Canvas, trim: str, page_num: int, dot_spacing_pt: float = 18) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    c.setFillColor(Color(0.7, 0.7, 0.7))
    y = y1
    while y > y0:
        x = x0
        while x < x1:
            c.circle(x, y, 0.6, fill=1, stroke=0)
            x += dot_spacing_pt
        y -= dot_spacing_pt
    c.setFillColor(black)


# ---------------------------------------------------------------------------
# Public builders
# ---------------------------------------------------------------------------


def build_lined_interior(
    out_path: Path,
    trim: str,
    page_count: int,
    title: str,
    subtitle: str,
    author: str,
    style: str = "lined",  # "lined" or "dotted"
) -> Path:
    """Build a simple lined or dot-grid journal interior."""
    tw, th = TRIM_SIZES[trim]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=(tw * 72, th * 72))

    # Page 1: title page.
    _draw_title_page(c, trim, title, subtitle, author)
    c.showPage()
    # Page 2: blank verso.
    c.showPage()
    # Page 3: "belongs to".
    _draw_belongs_to_page(c, trim)
    c.showPage()
    # Page 4: blank.
    c.showPage()

    # Remaining pages: lined.
    drawer = _draw_lined_page if style == "lined" else _draw_dotted_page
    for i in range(5, page_count + 1):
        drawer(c, trim, i)
        _draw_page_number(c, trim, i)
        c.showPage()

    c.save()
    return out_path


def build_prompt_journal_interior(
    out_path: Path,
    trim: str,
    page_count: int,
    title: str,
    subtitle: str,
    author: str,
    prompts: List[str],
) -> Path:
    """Prompt journal: title page, belongs-to, then alternating prompt+lined pages."""
    tw, th = TRIM_SIZES[trim]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=(tw * 72, th * 72))

    _draw_title_page(c, trim, title, subtitle, author)
    c.showPage()
    c.showPage()
    _draw_belongs_to_page(c, trim)
    c.showPage()
    c.showPage()

    pi = 0
    page_num = 5
    while page_num <= page_count and pi < len(prompts):
        # Top: prompt text. Bottom: lined writing area.
        x0, y0, x1, y1 = _content_box(trim, page_num)

        # Day/prompt number.
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(Color(0.4, 0.4, 0.4))
        c.drawString(x0, y1 - 6, f"PROMPT {pi + 1:03d}")
        c.setFillColor(black)

        # Prompt text box.
        c.setFont("Helvetica-Bold", 14)
        prompt_lines = _wrap_to_width(c, prompts[pi], "Helvetica-Bold", 14, x1 - x0)
        y = y1 - 28
        for line in prompt_lines[:4]:  # cap to 4 lines
            c.drawString(x0, y, line)
            y -= 18

        # Decorative divider.
        c.setStrokeColor(Color(0.6, 0.6, 0.6))
        c.setLineWidth(0.6)
        divider_y = y - 6
        c.line(x0, divider_y, x1, divider_y)

        # Lined writing area below divider.
        c.setStrokeColor(Color(0.78, 0.78, 0.78))
        c.setLineWidth(0.4)
        line_y = divider_y - 28
        while line_y > y0:
            c.line(x0, line_y, x1, line_y)
            line_y -= 22

        _draw_page_number(c, trim, page_num)
        c.showPage()
        page_num += 1
        pi += 1

    # If we run out of prompts but still have pages, fill with plain lined.
    while page_num <= page_count:
        _draw_lined_page(c, trim, page_num)
        _draw_page_number(c, trim, page_num)
        c.showPage()
        page_num += 1

    c.save()
    return out_path


def build_tracker_interior(
    out_path: Path,
    trim: str,
    page_count: int,
    title: str,
    subtitle: str,
    author: str,
) -> Path:
    """Habit tracker: title, setup pages, then 1 month-grid per page repeating."""
    tw, th = TRIM_SIZES[trim]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=(tw * 72, th * 72))

    _draw_title_page(c, trim, title, subtitle, author)
    c.showPage()
    c.showPage()

    # Setup page: "define your habits".
    x0, y0, x1, y1 = _content_box(trim, 3)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(black)
    c.drawString(x0, y1 - 24, "Define Your Habits")
    c.setFont("Helvetica", 11)
    c.drawString(x0, y1 - 44, "List 1-8 habits you want to track this month.")

    # Numbered lines.
    y = y1 - 76
    for n in range(1, 9):
        c.setFont("Helvetica", 12)
        c.drawString(x0, y, f"{n}.")
        c.setStrokeColor(Color(0.8, 0.8, 0.8))
        c.setLineWidth(0.5)
        c.line(x0 + 20, y - 2, x1, y - 2)
        y -= 30
    _draw_page_number(c, trim, 3)
    c.showPage()
    c.showPage()  # blank

    # Monthly grids.
    for page_num in range(5, page_count + 1):
        x0, y0, x1, y1 = _content_box(trim, page_num)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(black)
        c.drawString(x0, y1 - 22, "Month")
        c.setStrokeColor(Color(0.5, 0.5, 0.5))
        c.setLineWidth(0.6)
        c.line(x0 + 60, y1 - 24, x0 + 200, y1 - 24)

        # Grid: rows = 8 habits, cols = 1 wide label col + 31 narrow day cols.
        grid_top = y1 - 50
        grid_bottom = y0 + 30
        grid_left = x0
        grid_right = x1
        rows = 9   # 1 header + 8 habits
        day_cols = 31
        # Label col is 22% of width; day cols share the rest equally.
        total_w = grid_right - grid_left
        label_w = total_w * 0.22
        day_w = (total_w - label_w) / day_cols
        row_h = (grid_top - grid_bottom) / rows

        # Header row: "Habit" in label col, day numbers 1..31 in day cols.
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(black)
        c.drawString(grid_left + 4, grid_top - row_h * 0.65, "Habit")
        c.setFont("Helvetica", 7)
        for d in range(1, 32):
            cx = grid_left + label_w + day_w * (d - 0.5)
            c.drawCentredString(cx, grid_top - row_h * 0.65, str(d))

        # Lines.
        c.setStrokeColor(Color(0.7, 0.7, 0.7))
        c.setLineWidth(0.3)
        # Horizontal lines.
        for r in range(rows + 1):
            y = grid_top - row_h * r
            c.line(grid_left, y, grid_right, y)
        # Vertical lines: edges, label/day boundary, then each day col.
        c.line(grid_left, grid_top, grid_left, grid_bottom)
        c.line(grid_left + label_w, grid_top, grid_left + label_w, grid_bottom)
        for col in range(1, day_cols + 1):
            x = grid_left + label_w + day_w * col
            c.line(x, grid_top, x, grid_bottom)

        _draw_page_number(c, trim, page_num)
        c.showPage()

    c.save()
    return out_path


def build_wordsearch_interior(
    out_path: Path,
    trim: str,
    page_count: int,
    title: str,
    subtitle: str,
    author: str,
    puzzles: List[dict],
) -> Path:
    """Word search book: title, instructions, puzzles, then solutions at the back.

    `puzzles` items: {"theme": str, "words": [str,...], "grid": [[char,...],...],
                      "positions": {WORD: {"row": int, "col": int, "dir": str}}}.
    """
    tw, th = TRIM_SIZES[trim]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=(tw * 72, th * 72))
    page = 1  # tracks the *current* page we're drawing on

    # Page 1: title.
    _draw_title_page(c, trim, title, subtitle, author)
    c.showPage(); page += 1

    # Page 2: how to play.
    x0, y0, x1, y1 = _content_box(trim, page)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(black)
    c.drawString(x0, y1 - 24, "How to Play")
    c.setFont("Helvetica", 12)
    intro = (
        "Find each word from the list hidden in the grid. Words can run "
        "horizontally, vertically, or diagonally, forward or backward. "
        "Circle each word as you find it. Solutions are at the back of the book."
    )
    y = y1 - 50
    for line in _wrap_to_width(c, intro, "Helvetica", 12, x1 - x0):
        c.drawString(x0, y, line)
        y -= 16
    _draw_page_number(c, trim, page)
    c.showPage(); page += 1

    # Reserve at least 2 pages at the end for solutions (header + content).
    # Puzzles get whatever's left in between.
    min_solutions_pages = 2
    last_puzzle_page = page_count - min_solutions_pages

    drawn_puzzles = 0
    for i, puz in enumerate(puzzles):
        if page > last_puzzle_page:
            break
        x0, y0, x1, y1 = _content_box(trim, page)

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(black)
        c.drawString(x0, y1 - 18, f"Puzzle {i + 1}: {puz['theme']}")

        grid = puz["grid"]
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        grid_size = min(x1 - x0, (y1 - y0) * 0.6)
        cell = grid_size / max(rows, cols, 1)
        gx0 = x0 + ((x1 - x0) - cell * cols) / 2
        gy_top = y1 - 36

        c.setFont("Helvetica", max(8, int(cell * 0.6)))
        c.setStrokeColor(Color(0.85, 0.85, 0.85))
        c.setLineWidth(0.3)
        for r in range(rows):
            for col in range(cols):
                cx = gx0 + col * cell
                cy = gy_top - (r + 1) * cell
                c.rect(cx, cy, cell, cell, fill=0, stroke=1)
                c.drawCentredString(cx + cell / 2, cy + cell * 0.28, grid[r][col])

        # Word list below grid.
        words = puz["words"]
        c.setFont("Helvetica", 10)
        wl_top = gy_top - cell * rows - 22
        per_row = 4
        col_w = (x1 - x0) / per_row
        for wi, w in enumerate(words):
            row = wi // per_row
            col = wi % per_row
            c.drawString(x0 + col * col_w, wl_top - row * 14, w)

        _draw_page_number(c, trim, page)
        c.showPage(); page += 1
        drawn_puzzles += 1

    # Solutions follow immediately after the last puzzle — no padding waste.
    # Solutions header.
    if page <= page_count:
        x0, y0, x1, y1 = _content_box(trim, page)
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(black)
        c.drawString(x0, y1 - 30, "Solutions")
        c.setFont("Helvetica", 10)
        c.drawString(x0, y1 - 50, "Each entry shows the starting cell and direction of the hidden word.")
        _draw_page_number(c, trim, page)
        c.showPage(); page += 1

    # Solutions content — strictly bounded by page_count. Use 2 columns for density.
    if page <= page_count:
        x0, y0, x1, y1 = _content_box(trim, page)
        line_h = 10
        col_gap = 12
        col_w = (x1 - x0 - col_gap) / 2
        cur_col = 0
        col_x = [x0, x0 + col_w + col_gap]
        y = y1 - 14

        def _newpage_for_solutions():
            nonlocal page, x0, y0, x1, y1, col_x, col_w, y, cur_col
            _draw_page_number(c, trim, page)
            c.showPage(); page += 1
            if page > page_count:
                return False
            x0, y0, x1, y1 = _content_box(trim, page)
            col_w = (x1 - x0 - col_gap) / 2
            col_x = [x0, x0 + col_w + col_gap]
            y = y1 - 14
            cur_col = 0
            return True

        truncated = False
        for i, puz in enumerate(puzzles[:drawn_puzzles]):
            if page > page_count:
                truncated = True
                break

            block_lines = 1 + len(puz.get("positions", {}))
            block_h = block_lines * line_h + 4

            # If this block doesn't fit in current column, advance.
            if y - block_h < y0 + 10:
                if cur_col == 0:
                    cur_col = 1
                    y = y1 - 14
                else:
                    if not _newpage_for_solutions():
                        truncated = True
                        break

            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(black)
            c.drawString(col_x[cur_col], y, f"Puzzle {i + 1}: {puz['theme']}")
            y -= line_h
            c.setFont("Helvetica", 8)
            for w, pos in puz.get("positions", {}).items():
                c.drawString(col_x[cur_col] + 6, y,
                             f"{w} — r{pos['row']+1}, c{pos['col']+1}, {pos['dir']}")
                y -= line_h
            y -= 4

        if page <= page_count:
            _draw_page_number(c, trim, page)
            c.showPage(); page += 1

        if truncated:
            print(f"  [warn] Solutions truncated to fit page_count={page_count}.")

    # Pad to exact page_count.
    while page <= page_count:
        _draw_page_number(c, trim, page)
        c.showPage(); page += 1

    c.save()
    return out_path


# ---------------------------------------------------------------------------
# Diabetes daily log book
# ---------------------------------------------------------------------------

# What's actually in this book. Used by metadata.py to write accurate descriptions.
DIABETES_LOG_CONTENTS = """100-page diabetes daily log book with the following structure:

FRONT MATTER (8 pages):
- Title page
- "This logbook belongs to" page with emergency contact lines
- Starting baseline page (initial A1C, weight, BP, diagnosis date, current medications)
- "My 90-day goals" page with lined space for personal goals
- "My care team" page with template lines for GP, endocrinologist, dietitian, pharmacist names + phone numbers
- "How to use this book" instructions page

DAILY LOG PAGES (90 pages, one per day):
Each page contains:
- Date and day-of-week field at top
- Blood glucose table: 5 rows (Fasting, Breakfast, Lunch, Dinner, Bedtime) x 4 columns (Time, Pre-meal, Post-meal 2hr, Notes). Pre/post fields are blank for the buyer to write mmol/L or mg/dL readings.
- Carbs by meal row: Breakfast / Lunch / Dinner / Snacks / Total
- Medications row: 4 checkboxes (Morning / Noon / Evening / Bedtime) + insulin units field + notes
- Activity row: Type + Duration in minutes
- Other metrics row: Water (cups), Sleep (hours), Mood (1-10)
- "How I felt today" notes section (4 lined rows)

BACK MATTER (2 pages):
- A1C trend log (table with date / A1C / weight / notes columns for periodic readings)
- Notes / questions page (lined)

Does NOT contain: diagnostic flowcharts, treatment recommendations, dose calculators,
food databases, or any specific medical advice. It is a TRACKING tool for the buyer
to fill in their own readings, to share with their care team."""


def _draw_checkbox(c: canvas.Canvas, x: float, y: float, size: float = 9) -> None:
    """Empty square checkbox at (x,y)."""
    c.setStrokeColor(black)
    c.setLineWidth(0.6)
    c.rect(x, y, size, size, fill=0, stroke=1)


def _draw_field_underline(c: canvas.Canvas, x: float, y: float, width: float) -> None:
    c.setStrokeColor(Color(0.65, 0.65, 0.65))
    c.setLineWidth(0.4)
    c.line(x, y, x + width, y)


def _draw_section_label(c: canvas.Canvas, label: str, x: float, y: float, size: int = 8) -> None:
    c.setFont("Helvetica-Bold", size)
    c.setFillColor(Color(0.35, 0.35, 0.35))
    c.drawString(x, y, label.upper())
    c.setFillColor(black)


def _draw_diabetes_daily_page(c: canvas.Canvas, trim: str, page_num: int, day_num: int) -> None:
    """Render one daily log page. Designed for 6x9 trim."""
    x0, y0, x1, y1 = _content_box(trim, page_num)
    content_w = x1 - x0
    cur_y = y1

    # ===== Header: DAY N + DATE/WEEKDAY =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 14, f"DAY {day_num:03d}")
    # Date and weekday on right
    c.setFont("Helvetica", 10)
    c.setFillColor(Color(0.45, 0.45, 0.45))
    c.drawRightString(x1, cur_y - 14, "Date: __________   Weekday: ____")
    cur_y -= 26

    # Thin divider under header.
    c.setStrokeColor(Color(0.7, 0.7, 0.7))
    c.setLineWidth(0.5)
    c.line(x0, cur_y, x1, cur_y)
    cur_y -= 14

    # ===== Blood glucose table =====
    _draw_section_label(c, "Blood glucose (mmol/L or mg/dL)", x0, cur_y - 2)
    cur_y -= 14

    # Table dimensions.
    row_h = 16
    rows = ["Fasting", "Breakfast", "Lunch", "Dinner", "Bedtime"]
    n_rows = len(rows) + 1  # +1 header
    table_h = row_h * n_rows
    # Column widths (totals must equal content_w).
    col_time = content_w * 0.22
    col_pre = content_w * 0.16
    col_post = content_w * 0.18
    col_notes = content_w - col_time - col_pre - col_post
    cols = [col_time, col_pre, col_post, col_notes]
    col_x = [x0]
    for w in cols:
        col_x.append(col_x[-1] + w)

    table_top = cur_y
    table_bottom = cur_y - table_h
    # Outer box.
    c.setStrokeColor(Color(0.55, 0.55, 0.55))
    c.setLineWidth(0.6)
    c.rect(x0, table_bottom, content_w, table_h, fill=0, stroke=1)
    # Horizontal lines.
    for i in range(1, n_rows):
        y = table_top - row_h * i
        c.setLineWidth(0.4)
        c.line(x0, y, x1, y)
    # Vertical lines.
    for cx in col_x[1:-1]:
        c.line(cx, table_top, cx, table_bottom)

    # Header row text.
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(black)
    headers = ["Time", "Pre-meal", "Post 2hr", "Notes"]
    for i, h in enumerate(headers):
        c.drawString(col_x[i] + 4, table_top - row_h + 5, h)

    # Time-label rows.
    c.setFont("Helvetica", 9)
    for i, label in enumerate(rows):
        row_y = table_top - row_h * (i + 2) + 5
        c.drawString(col_x[0] + 4, row_y, label)
        # Post column for Fasting and Bedtime shows a dash (no post-meal reading).
        if label in ("Fasting", "Bedtime"):
            c.setFillColor(Color(0.6, 0.6, 0.6))
            c.drawCentredString((col_x[2] + col_x[3]) / 2, row_y, "—")
            c.setFillColor(black)

    cur_y = table_bottom - 12

    # ===== Carbs by meal =====
    _draw_section_label(c, "Carbs by meal (grams)", x0, cur_y - 2)
    cur_y -= 12
    c.setFont("Helvetica", 9)
    parts = [("Breakfast", 0.20), ("Lunch", 0.20), ("Dinner", 0.20), ("Snacks", 0.20), ("Total", 0.20)]
    px = x0
    for name, frac in parts:
        c.drawString(px, cur_y, f"{name}:")
        underline_x = px + c.stringWidth(f"{name}:", "Helvetica", 9) + 4
        underline_w = content_w * frac - (underline_x - px) - 6
        _draw_field_underline(c, underline_x, cur_y - 2, underline_w)
        px += content_w * frac
    cur_y -= 14

    # ===== Medications =====
    _draw_section_label(c, "Medications taken", x0, cur_y - 2)
    cur_y -= 14
    c.setFont("Helvetica", 9)
    boxes = ["Morning", "Noon", "Evening", "Bedtime"]
    box_x = x0
    for label in boxes:
        _draw_checkbox(c, box_x, cur_y - 2, size=9)
        c.drawString(box_x + 13, cur_y, label)
        box_x += c.stringWidth(label, "Helvetica", 9) + 30
    cur_y -= 14
    # Insulin units + notes line.
    c.drawString(x0, cur_y, "Insulin units:")
    iw_x = x0 + c.stringWidth("Insulin units:", "Helvetica", 9) + 4
    _draw_field_underline(c, iw_x, cur_y - 2, 50)
    c.drawString(iw_x + 60, cur_y, "Notes:")
    nx = iw_x + 60 + c.stringWidth("Notes:", "Helvetica", 9) + 4
    _draw_field_underline(c, nx, cur_y - 2, x1 - nx)
    cur_y -= 16

    # ===== Activity =====
    _draw_section_label(c, "Activity", x0, cur_y - 2)
    cur_y -= 12
    c.setFont("Helvetica", 9)
    c.drawString(x0, cur_y, "Type:")
    type_x = x0 + c.stringWidth("Type:", "Helvetica", 9) + 4
    type_w = content_w * 0.5 - (type_x - x0)
    _draw_field_underline(c, type_x, cur_y - 2, type_w)
    dur_label_x = x0 + content_w * 0.55
    c.drawString(dur_label_x, cur_y, "Duration (min):")
    dur_field_x = dur_label_x + c.stringWidth("Duration (min):", "Helvetica", 9) + 4
    _draw_field_underline(c, dur_field_x, cur_y - 2, x1 - dur_field_x)
    cur_y -= 14

    # ===== Other metrics =====
    _draw_section_label(c, "Other", x0, cur_y - 2)
    cur_y -= 12
    c.setFont("Helvetica", 9)
    others = [("Water (cups):", 0.30), ("Sleep (hrs):", 0.30), ("Mood (1-10):", 0.40)]
    px = x0
    for name, frac in others:
        c.drawString(px, cur_y, name)
        lx = px + c.stringWidth(name, "Helvetica", 9) + 4
        lw = content_w * frac - (lx - px) - 8
        _draw_field_underline(c, lx, cur_y - 2, lw)
        px += content_w * frac
    cur_y -= 16

    # ===== Notes =====
    _draw_section_label(c, "How I felt today", x0, cur_y - 2)
    cur_y -= 12
    c.setStrokeColor(Color(0.7, 0.7, 0.7))
    c.setLineWidth(0.35)
    # Draw a few lined writing rows.
    while cur_y > y0 + 12:
        c.line(x0, cur_y, x1, cur_y)
        cur_y -= 18


def _draw_belongs_to_page_diabetes(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 26, "This logbook belongs to")
    cur_y -= 50

    fields = [
        ("Name", 0.85),
        ("Diagnosed", 0.45),
        ("Date started this logbook", 0.45),
        ("Emergency contact (name)", 0.85),
        ("Emergency contact (phone)", 0.55),
    ]
    c.setFont("Helvetica", 11)
    for label, frac in fields:
        c.drawString(x0, cur_y, f"{label}:")
        lx = x0 + c.stringWidth(f"{label}:", "Helvetica", 11) + 6
        lw = (x1 - x0) * frac - (lx - x0)
        _draw_field_underline(c, lx, cur_y - 3, lw)
        cur_y -= 26

    _draw_page_number(c, trim, page_num)


def _draw_baseline_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 24, "My starting baseline")
    cur_y -= 36

    c.setFont("Helvetica", 10)
    c.setFillColor(Color(0.4, 0.4, 0.4))
    c.drawString(x0, cur_y, "Record these the day you start the logbook. Update at each follow-up.")
    c.setFillColor(black)
    cur_y -= 26

    c.setFont("Helvetica", 11)
    items = [
        "Date diagnosed:",
        "Most recent A1C (%) and date:",
        "Fasting glucose today:",
        "Weight (kg or lb):",
        "Blood pressure:",
        "Current medications (one per line):",
        "  ",
        "  ",
        "  ",
        "Other conditions to know about:",
        "  ",
        "Allergies:",
        "  ",
        "Doctor or clinic I see for diabetes:",
    ]
    for label in items:
        c.drawString(x0, cur_y, label)
        lx = x0 + c.stringWidth(label, "Helvetica", 11) + 6
        _draw_field_underline(c, lx, cur_y - 3, x1 - lx)
        cur_y -= 22
        if cur_y < y0 + 20:
            break

    _draw_page_number(c, trim, page_num)


def _draw_goals_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 24, "My 90-day goals")
    cur_y -= 36

    c.setFont("Helvetica", 10)
    c.setFillColor(Color(0.4, 0.4, 0.4))
    intro = (
        "Set 2-4 specific, doable goals for the next three months. Examples: "
        "'A1C below 7.0', 'Walk 20 minutes after dinner', 'Carbs under 60g per meal'."
    )
    for line in _wrap_to_width(c, intro, "Helvetica", 10, x1 - x0):
        c.drawString(x0, cur_y, line)
        cur_y -= 13
    c.setFillColor(black)
    cur_y -= 14

    # 4 numbered goal blocks.
    c.setFont("Helvetica", 11)
    for i in range(1, 5):
        c.drawString(x0, cur_y, f"Goal {i}:")
        lx = x0 + c.stringWidth(f"Goal {i}:", "Helvetica", 11) + 6
        _draw_field_underline(c, lx, cur_y - 3, x1 - lx)
        cur_y -= 18
        # 2 extra lined rows for notes/why.
        for _ in range(2):
            _draw_field_underline(c, x0, cur_y - 3, x1 - x0)
            cur_y -= 18
        cur_y -= 6
        if cur_y < y0 + 20:
            break

    _draw_page_number(c, trim, page_num)


def _draw_care_team_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 24, "My care team")
    cur_y -= 36

    roles = [
        "General practitioner / family doctor",
        "Diabetes specialist or endocrinologist",
        "Diabetes nurse educator",
        "Dietitian",
        "Pharmacist",
        "Eye care (optometrist / ophthalmologist)",
        "Podiatrist",
        "Other:",
    ]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, cur_y, "Role")
    c.drawString(x0 + (x1 - x0) * 0.45, cur_y, "Name")
    c.drawString(x0 + (x1 - x0) * 0.78, cur_y, "Phone")
    cur_y -= 16

    c.setFont("Helvetica", 10)
    for role in roles:
        c.drawString(x0, cur_y, role)
        _draw_field_underline(c, x0 + (x1 - x0) * 0.45, cur_y - 3, (x1 - x0) * 0.30)
        _draw_field_underline(c, x0 + (x1 - x0) * 0.78, cur_y - 3, (x1 - x0) * 0.22)
        cur_y -= 26

    _draw_page_number(c, trim, page_num)


def _draw_how_to_use_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 20)
    c.drawString(x0, cur_y - 24, "How to use this book")
    cur_y -= 38

    c.setFont("Helvetica", 11)
    sections = [
        ("One page per day.",
         "Each daily page has space for your blood glucose readings, carbs at each meal, "
         "medications taken, activity, sleep, and mood. Fill it in as you go through the day."),
        ("Use the units you and your doctor use.",
         "The book leaves space for either mmol/L or mg/dL. Pick one and stick with it."),
        ("Be honest with the numbers.",
         "The pattern over weeks matters more than any single reading. Days you 'forgot' "
         "to log are fine — leave them blank and pick up tomorrow."),
        ("Bring it to your appointments.",
         "Your doctor, nurse, or dietitian can see in seconds what your numbers look like "
         "across the week. That's more useful than a meter download."),
        ("Use the back A1C log for the long view.",
         "Every time you get a new A1C result, write it in the table at the back of the book."),
        ("Not medical advice.",
         "This logbook is a tool for you to record and share your own readings. "
         "Any decisions about medication, diet, or activity belong with your healthcare team."),
    ]
    for heading, body in sections:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x0, cur_y, heading)
        cur_y -= 14
        c.setFont("Helvetica", 10)
        for line in _wrap_to_width(c, body, "Helvetica", 10, x1 - x0):
            c.drawString(x0, cur_y, line)
            cur_y -= 12
        cur_y -= 6
        if cur_y < y0 + 20:
            break

    _draw_page_number(c, trim, page_num)


def _draw_a1c_log_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x0, cur_y - 22, "A1C and clinical results log")
    cur_y -= 32

    c.setFont("Helvetica", 10)
    c.setFillColor(Color(0.4, 0.4, 0.4))
    c.drawString(x0, cur_y, "Update each time you get new lab results. Brings the long view into focus.")
    c.setFillColor(black)
    cur_y -= 18

    # Table: Date | A1C (%) | Fasting | Weight | BP | Notes
    headers = ["Date", "A1C %", "Fasting", "Weight", "BP", "Notes"]
    fracs   = [0.13,   0.10,   0.13,      0.13,    0.14, 0.37]
    content_w = x1 - x0
    col_x = [x0]
    for f in fracs:
        col_x.append(col_x[-1] + content_w * f)

    row_h = 22
    n_rows = 14  # 1 header + 13 data
    table_top = cur_y
    table_h = row_h * n_rows
    table_bottom = cur_y - table_h
    c.setStrokeColor(Color(0.55, 0.55, 0.55))
    c.setLineWidth(0.5)
    c.rect(x0, table_bottom, content_w, table_h, fill=0, stroke=1)
    for i in range(1, n_rows):
        y = table_top - row_h * i
        c.setLineWidth(0.3)
        c.line(x0, y, x1, y)
    for cx in col_x[1:-1]:
        c.line(cx, table_top, cx, table_bottom)

    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawString(col_x[i] + 4, table_top - row_h + 6, h)

    _draw_page_number(c, trim, page_num)


def _draw_notes_page(c: canvas.Canvas, trim: str, page_num: int, heading: str = "Notes & questions") -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x0, y1 - 18, heading)
    c.setStrokeColor(Color(0.7, 0.7, 0.7))
    c.setLineWidth(0.35)
    line_y = y1 - 44
    while line_y > y0 + 12:
        c.line(x0, line_y, x1, line_y)
        line_y -= 22
    _draw_page_number(c, trim, page_num)


def build_diabetes_log_interior(
    out_path: Path,
    trim: str,
    page_count: int,
    title: str,
    subtitle: str,
    author: str,
) -> Path:
    """Build a clinical-grade 90-day diabetes daily log book.

    Page layout (for page_count=100):
        1  Title page
        2  blank verso
        3  Belongs to + emergency contacts
        4  blank
        5  Starting baseline (A1C, weight, BP, meds, diagnosis date)
        6  blank
        7  90-day goals
        8  blank
        9  Care team
        10 How to use this book
        11-100  Daily log pages (one per day; 90 if page_count=100)
        Last 2  A1C log + notes page
    """
    tw, th = TRIM_SIZES[trim]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=(tw * 72, th * 72))

    page = 1
    # Title page.
    _draw_title_page(c, trim, title, subtitle, author)
    c.showPage(); page += 1
    # Verso.
    c.showPage(); page += 1

    # Belongs to.
    _draw_belongs_to_page_diabetes(c, trim, page)
    c.showPage(); page += 1
    c.showPage(); page += 1  # blank

    # Baseline.
    _draw_baseline_page(c, trim, page)
    c.showPage(); page += 1
    c.showPage(); page += 1

    # Goals.
    _draw_goals_page(c, trim, page)
    c.showPage(); page += 1
    c.showPage(); page += 1

    # Care team.
    _draw_care_team_page(c, trim, page)
    c.showPage(); page += 1

    # How to use.
    _draw_how_to_use_page(c, trim, page)
    c.showPage(); page += 1

    # Reserve last 2 pages for A1C log + notes.
    end_reserve = 2
    last_daily_page = page_count - end_reserve

    # Daily log pages.
    day = 1
    while page <= last_daily_page:
        _draw_diabetes_daily_page(c, trim, page, day_num=day)
        _draw_page_number(c, trim, page)
        c.showPage(); page += 1
        day += 1

    # Back matter.
    if page <= page_count:
        _draw_a1c_log_page(c, trim, page)
        c.showPage(); page += 1
    if page <= page_count:
        _draw_notes_page(c, trim, page, heading="Notes & questions for my care team")
        c.showPage(); page += 1

    # Pad if short.
    while page <= page_count:
        _draw_page_number(c, trim, page)
        c.showPage(); page += 1

    c.save()
    return out_path


# ---------------------------------------------------------------------------
# Adult ADHD daily planner
# ---------------------------------------------------------------------------

ADHD_PLANNER_CONTENTS = """100-page adult ADHD daily planner with the following structure:

FRONT MATTER (8 pages):
- Title page
- "This planner belongs to" page with emergency contact lines
- "My ADHD profile" baseline page (diagnosis date, comorbidities, current
  stimulant + non-stimulant medications with doses, what I'm working on)
- "My 90-day goals" page with 4 numbered goal blocks + notes lines
- "My care team" page with role/name/phone rows (psychiatrist, therapist,
  ADHD coach, GP, prescribing pharmacist)
- "How to use this planner" page explaining the daily structure and the
  underlying principles (top-3 priorities, distraction parking, daily wins)

DAILY PAGES (88 pages, one per day):
Each page is intentionally designed for executive-function support, not
generic productivity planning. Each contains:
- DAY header with date and weekday fields
- TOP 3 PRIORITIES (not a long todo list — cap at three)
- MEDS row: stimulant checkbox + time + dose field; non-stimulant notes
- TIME BLOCKS: 8 realistic-sized chunks (morning through evening) with
  one-line space each (not 15-minute granularity that ADHD brains can't
  sustain)
- FOCUS / ENERGY row: morning, midday, evening rating (1-5 scale)
- BODY row: movement minutes + last night sleep hours
- DISTRACTION PARK: 4 lined slots to capture intrusive thoughts/ideas
  during deep work, so they can be addressed later without breaking flow
- END OF DAY: today's win, one lesson, what to carry to tomorrow

BACK MATTER (4 pages):
- Medication trial log (table: med name, dose, start date, effects,
  side effects, stopped date)
- 90-day reflection page (lined: what worked, what didn't, next focus)
- Notes pages (2)

Does NOT contain: dose calculators, treatment recommendations, diagnostic
criteria, or specific clinical advice. It is a PERSONAL planning and
tracking tool. The disclaimer page makes this explicit."""


def _draw_adhd_belongs_to_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 26, "This planner belongs to")
    cur_y -= 50

    fields = [
        ("Name", 0.85),
        ("Diagnosed", 0.45),
        ("Date started this planner", 0.45),
        ("Emergency contact (name)", 0.85),
        ("Emergency contact (phone)", 0.55),
    ]
    c.setFont("Helvetica", 11)
    for label, frac in fields:
        c.drawString(x0, cur_y, f"{label}:")
        lx = x0 + c.stringWidth(f"{label}:", "Helvetica", 11) + 6
        lw = (x1 - x0) * frac - (lx - x0)
        _draw_field_underline(c, lx, cur_y - 3, lw)
        cur_y -= 26

    _draw_page_number(c, trim, page_num)


def _draw_adhd_profile_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 24, "My ADHD profile")
    cur_y -= 36

    c.setFont("Helvetica", 10)
    c.setFillColor(Color(0.4, 0.4, 0.4))
    c.drawString(x0, cur_y, "A quick snapshot. Update at appointments or when meds change.")
    c.setFillColor(black)
    cur_y -= 24

    c.setFont("Helvetica", 11)
    items = [
        "Date diagnosed:",
        "Diagnosing clinician:",
        "Presentation (inattentive / hyperactive / combined):",
        "Other diagnoses (anxiety, depression, ASD, etc.):",
        "Current stimulant medication and dose:",
        "Current non-stimulant medication and dose:",
        "Other medications:",
        "What I'm working on right now (one sentence):",
        "  ",
        "What helps me most when I'm overwhelmed:",
        "  ",
        "My biggest current struggle:",
        "  ",
    ]
    for label in items:
        c.drawString(x0, cur_y, label)
        lx = x0 + c.stringWidth(label, "Helvetica", 11) + 6
        _draw_field_underline(c, lx, cur_y - 3, x1 - lx)
        cur_y -= 22
        if cur_y < y0 + 20:
            break

    _draw_page_number(c, trim, page_num)


def _draw_adhd_care_team_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 24, "My care team")
    cur_y -= 36

    roles = [
        "Psychiatrist / prescribing clinician",
        "Therapist / psychologist",
        "ADHD coach",
        "General practitioner / family doctor",
        "Pharmacist",
        "Other (workplace / education support):",
        "Other:",
    ]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, cur_y, "Role")
    c.drawString(x0 + (x1 - x0) * 0.45, cur_y, "Name")
    c.drawString(x0 + (x1 - x0) * 0.78, cur_y, "Phone")
    cur_y -= 16

    c.setFont("Helvetica", 10)
    for role in roles:
        c.drawString(x0, cur_y, role)
        _draw_field_underline(c, x0 + (x1 - x0) * 0.45, cur_y - 3, (x1 - x0) * 0.30)
        _draw_field_underline(c, x0 + (x1 - x0) * 0.78, cur_y - 3, (x1 - x0) * 0.22)
        cur_y -= 26

    _draw_page_number(c, trim, page_num)


def _draw_adhd_how_to_use_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 20)
    c.drawString(x0, cur_y - 24, "How to use this planner")
    cur_y -= 38

    sections = [
        ("Top 3 — and only 3.",
         "Long todo lists overwhelm an ADHD brain and stop being motivating "
         "after about 15 minutes. Pick three things. If they're done, you "
         "had a good day. Tomorrow gets its own three."),
        ("Distraction park is your second brain.",
         "When a thought interrupts you mid-task ('I should email Joe', "
         "'we need milk', 'what if I rewrite the project plan'), write it "
         "in the park box and go back to the task. The thought is safe; "
         "you'll come back to it."),
        ("Time blocks are not appointments.",
         "These are loose containers, not commitments. A 9-10 block that "
         "becomes 9-11 isn't failure — it's information about how long "
         "things actually take you."),
        ("Track meds honestly.",
         "Forgetting your stimulant is not a moral failure; it's data. "
         "Patterns over weeks help you and your prescriber adjust."),
        ("End the day with a win, every day.",
         "ADHD brains forget what they accomplished and amplify what they "
         "didn't. The 'today's win' line fights that. The win can be tiny "
         "(showered, replied to one email). Write it anyway."),
        ("This is a planner, not medical advice.",
         "Decisions about diagnosis, medication, or therapy belong with "
         "your prescribing clinician."),
    ]
    c.setFont("Helvetica", 11)
    for heading, body in sections:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x0, cur_y, heading)
        cur_y -= 14
        c.setFont("Helvetica", 10)
        for line in _wrap_to_width(c, body, "Helvetica", 10, x1 - x0):
            c.drawString(x0, cur_y, line)
            cur_y -= 12
        cur_y -= 6
        if cur_y < y0 + 20:
            break

    _draw_page_number(c, trim, page_num)


def _draw_adhd_daily_page(c: canvas.Canvas, trim: str, page_num: int, day_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    content_w = x1 - x0
    cur_y = y1

    # Header: DAY N + date/weekday
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(x0, cur_y - 14, f"DAY {day_num:03d}")
    c.setFont("Helvetica", 10)
    c.setFillColor(Color(0.45, 0.45, 0.45))
    c.drawRightString(x1, cur_y - 14, "Date: __________   Weekday: ____")
    cur_y -= 24

    c.setStrokeColor(Color(0.7, 0.7, 0.7))
    c.setLineWidth(0.5)
    c.line(x0, cur_y, x1, cur_y)
    cur_y -= 14

    # Top 3 priorities
    _draw_section_label(c, "Today's 3 priorities", x0, cur_y - 2)
    cur_y -= 14
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    for n in range(1, 4):
        c.drawString(x0, cur_y, f"{n}.")
        _draw_field_underline(c, x0 + 16, cur_y - 3, content_w - 16)
        cur_y -= 18
    cur_y -= 4

    # Meds
    _draw_section_label(c, "Meds", x0, cur_y - 2)
    cur_y -= 14
    c.setFont("Helvetica", 10)
    _draw_checkbox(c, x0, cur_y - 1, size=9)
    c.drawString(x0 + 13, cur_y, "Stimulant taken")
    time_x = x0 + 13 + c.stringWidth("Stimulant taken", "Helvetica", 10) + 16
    c.drawString(time_x, cur_y, "Time:")
    tfield = time_x + c.stringWidth("Time:", "Helvetica", 10) + 4
    _draw_field_underline(c, tfield, cur_y - 2, 50)
    dose_x = tfield + 58
    c.drawString(dose_x, cur_y, "Dose:")
    dfield = dose_x + c.stringWidth("Dose:", "Helvetica", 10) + 4
    _draw_field_underline(c, dfield, cur_y - 2, x1 - dfield)
    cur_y -= 14
    c.drawString(x0, cur_y, "Other meds / notes:")
    n_field = x0 + c.stringWidth("Other meds / notes:", "Helvetica", 10) + 6
    _draw_field_underline(c, n_field, cur_y - 2, x1 - n_field)
    cur_y -= 14

    # Time blocks
    _draw_section_label(c, "Time blocks (loose, not appointments)", x0, cur_y - 2)
    cur_y -= 14
    blocks = ["AM 1", "AM 2", "AM 3", "Midday", "PM 1", "PM 2", "PM 3", "Evening"]
    c.setFont("Helvetica", 10)
    for label in blocks:
        c.drawString(x0, cur_y, f"{label}:")
        lw_x = x0 + c.stringWidth(f"{label}:", "Helvetica", 10) + 6
        _draw_field_underline(c, lw_x, cur_y - 2, x1 - lw_x)
        cur_y -= 17
    cur_y -= 2

    # Focus & energy — 3 fields on one row
    _draw_section_label(c, "Focus & energy (1-5)", x0, cur_y - 2)
    cur_y -= 13
    c.setFont("Helvetica", 10)
    third = content_w / 3
    for i, label in enumerate(["Morning:", "Midday:", "Evening:"]):
        px_ = x0 + i * third
        c.drawString(px_, cur_y, label)
        lx = px_ + c.stringWidth(label, "Helvetica", 10) + 4
        lw = third - (lx - px_) - 6
        _draw_field_underline(c, lx, cur_y - 2, lw)
    cur_y -= 16

    # Body — movement + sleep on its own row
    _draw_section_label(c, "Body", x0, cur_y - 2)
    cur_y -= 13
    c.setFont("Helvetica", 10)
    half = content_w / 2
    for i, label in enumerate(["Move (min):", "Sleep (hrs):"]):
        px_ = x0 + i * half
        c.drawString(px_, cur_y, label)
        lx = px_ + c.stringWidth(label, "Helvetica", 10) + 4
        lw = half - (lx - px_) - 6
        _draw_field_underline(c, lx, cur_y - 2, lw)
    cur_y -= 16

    # Distraction park
    _draw_section_label(c, "Distraction park (write it down, come back later)", x0, cur_y - 2)
    cur_y -= 13
    for _ in range(4):
        _draw_field_underline(c, x0, cur_y - 2, content_w)
        cur_y -= 14
    cur_y -= 2

    # End of day
    _draw_section_label(c, "End of day", x0, cur_y - 2)
    cur_y -= 13
    c.setFont("Helvetica", 10)
    for label in ["Today's win:", "One lesson:", "Carry to tomorrow:"]:
        c.drawString(x0, cur_y, label)
        lx = x0 + c.stringWidth(label, "Helvetica", 10) + 6
        _draw_field_underline(c, lx, cur_y - 2, x1 - lx)
        cur_y -= 16


def _draw_med_trial_page(c: canvas.Canvas, trim: str, page_num: int) -> None:
    x0, y0, x1, y1 = _content_box(trim, page_num)
    cur_y = y1

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x0, cur_y - 22, "Medication trial log")
    cur_y -= 32

    c.setFont("Helvetica", 10)
    c.setFillColor(Color(0.4, 0.4, 0.4))
    c.drawString(x0, cur_y, "Each row: a medication you've trialled. Bring this to your prescriber.")
    c.setFillColor(black)
    cur_y -= 18

    headers = ["Med + dose", "Started", "Stopped", "Effects", "Side effects"]
    fracs   = [0.26,         0.12,      0.12,      0.25,      0.25]
    content_w = x1 - x0
    col_x = [x0]
    for f in fracs:
        col_x.append(col_x[-1] + content_w * f)

    row_h = 28
    n_rows = 12
    table_top = cur_y
    table_h = row_h * n_rows
    table_bottom = cur_y - table_h
    c.setStrokeColor(Color(0.55, 0.55, 0.55))
    c.setLineWidth(0.5)
    c.rect(x0, table_bottom, content_w, table_h, fill=0, stroke=1)
    for i in range(1, n_rows):
        y = table_top - row_h * i
        c.setLineWidth(0.3)
        c.line(x0, y, x1, y)
    for cx in col_x[1:-1]:
        c.line(cx, table_top, cx, table_bottom)

    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawString(col_x[i] + 4, table_top - row_h + 8, h)

    _draw_page_number(c, trim, page_num)


def build_adhd_planner_interior(
    out_path: Path,
    trim: str,
    page_count: int,
    title: str,
    subtitle: str,
    author: str,
) -> Path:
    """Build a clinical-grade 90-day adult ADHD daily planner.

    For page_count=100:
        1  Title
        2  blank verso
        3  Belongs to + emergency contact
        4  My ADHD profile
        5  My 90-day goals
        6  My care team
        7  How to use this planner
        8  blank
        9-96  Daily pages (88 days)
        97 Medication trial log
        98 90-day reflection (lined notes)
        99-100  Notes pages
    """
    tw, th = TRIM_SIZES[trim]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=(tw * 72, th * 72))

    page = 1
    _draw_title_page(c, trim, title, subtitle, author)
    c.showPage(); page += 1
    c.showPage(); page += 1  # blank verso

    _draw_adhd_belongs_to_page(c, trim, page)
    c.showPage(); page += 1

    _draw_adhd_profile_page(c, trim, page)
    c.showPage(); page += 1

    _draw_goals_page(c, trim, page)
    c.showPage(); page += 1

    _draw_adhd_care_team_page(c, trim, page)
    c.showPage(); page += 1

    _draw_adhd_how_to_use_page(c, trim, page)
    c.showPage(); page += 1
    c.showPage(); page += 1  # blank

    # Reserve last 4 pages for back matter.
    end_reserve = 4
    last_daily_page = page_count - end_reserve

    day = 1
    while page <= last_daily_page:
        _draw_adhd_daily_page(c, trim, page, day_num=day)
        _draw_page_number(c, trim, page)
        c.showPage(); page += 1
        day += 1

    if page <= page_count:
        _draw_med_trial_page(c, trim, page)
        c.showPage(); page += 1
    if page <= page_count:
        _draw_notes_page(c, trim, page, heading="90-day reflection")
        c.showPage(); page += 1
    while page <= page_count:
        _draw_notes_page(c, trim, page, heading="Notes")
        c.showPage(); page += 1

    c.save()
    return out_path
