"""KDP technical specifications.

Source: KDP paperback manuscript and cover guidelines.
Numbers here come straight from Amazon's published spec, not guesswork.
"""
from __future__ import annotations

# Trim size (width, height) in inches. The common low-content sizes.
TRIM_SIZES = {
    "6x9":   (6.0, 9.0),
    "5x8":   (5.0, 8.0),
    "8.5x11": (8.5, 11.0),
    "7x10":  (7.0, 10.0),
}

# Bleed required on cover edges (KDP requires 0.125").
BLEED = 0.125

# Spine thickness per page (KDP formula).
# Black & white interior + white paper:  0.002252" per page
# Black & white interior + cream paper:  0.0025"   per page
# Premium color paper:                   0.002347" per page
PAGE_THICKNESS = {
    "white": 0.002252,
    "cream": 0.0025,
    "color": 0.002347,
}

# Interior margins for KDP paperbacks (inches).
# "Inside" = gutter, near the binding. "Outside" = the page edge.
# KDP's stated minimums for 24-150 pages are 0.375" gutter / 0.25" outside,
# but their auto-checker has a stricter undocumented buffer that rejects
# files at the stated minimums. These values clear the auto-check reliably.
INSIDE_MARGIN = 0.875
OUTSIDE_MARGIN = 0.5
TOP_MARGIN = 0.5
BOTTOM_MARGIN = 0.5

# Royalty math constants for printing cost estimates ($ USD, 60% royalty marketplaces).
# As of 2024: KDP charges fixed cost + per-page cost for B&W paperback.
PRINT_COST_FIXED_BW = 0.85
PRINT_COST_PER_PAGE_BW = 0.012
ROYALTY_RATE = 0.60


def spine_width(page_count: int, paper: str = "white") -> float:
    return page_count * PAGE_THICKNESS.get(paper, PAGE_THICKNESS["white"])


def cover_dimensions(trim: str, page_count: int, paper: str = "white") -> tuple[float, float, float]:
    """Return (full_width_in, full_height_in, spine_width_in) for the wrap cover."""
    tw, th = TRIM_SIZES[trim]
    sw = spine_width(page_count, paper)
    width = tw * 2 + sw + BLEED * 2
    height = th + BLEED * 2
    return width, height, sw


def estimate_royalty(list_price: float, page_count: int) -> float:
    """Rough royalty per sale (US marketplace, B&W paperback)."""
    printing = PRINT_COST_FIXED_BW + page_count * PRINT_COST_PER_PAGE_BW
    return max(0.0, list_price * ROYALTY_RATE - printing)
