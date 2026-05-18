"""Etsy listing copy generator.

Etsy rules (paste-friendly output respects all of these):
- Title: <= 140 characters. Front-load the keyword. Avoid repeating words.
- Tags: exactly 13 allowed; each <= 20 chars; multi-word tags rank better
  than single keywords; no punctuation.
- Description: first 160 chars matter for search snippet preview.
"""

from dataclasses import dataclass
from .themes import Theme


@dataclass
class Listing:
    title: str          # <= 140 chars
    tags: list[str]     # exactly 13, each <= 20 chars
    description: str
    materials: list[str]
    suggested_price_usd: float
    sku: str


def _truncate(s: str, limit: int) -> str:
    if len(s) <= limit:
        return s
    cut = s[:limit].rsplit(" ", 1)[0]
    return cut


def _dedupe(items):
    seen, out = set(), []
    for x in items:
        k = x.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(x)
    return out


def build_listing(
    planner_display_name: str,
    planner_keywords: tuple[str, ...],
    theme: Theme,
    sku: str,
    page_count: int = 1,
) -> Listing:
    primary_kw = planner_keywords[0]
    mood = theme.mood_words[0]

    # ----- TITLE -----
    raw_title = (
        f"{theme.display_name} {planner_display_name} Printable | "
        f"{primary_kw.title()} PDF | "
        f"Undated Instant Download | US Letter"
    )
    title = _truncate(raw_title, 140)

    # ----- TAGS (13, each <=20 chars, multi-word preferred) -----
    tag_pool = [
        *planner_keywords,
        f"{mood} planner",
        f"{mood} printable",
        "printable pdf",
        "instant download",
        "digital download",
        "us letter",
        "productivity",
        "minimalist",
        "self care",
    ]
    tag_pool = _dedupe(tag_pool)
    tags = []
    for t in tag_pool:
        t = t.strip().lower()
        if len(t) <= 20 and t not in tags:
            tags.append(t)
        if len(tags) == 13:
            break
    # pad if short
    fillers = ["planner pdf", "to do list", "weekly planner",
               "daily routine", "agenda template", "printable planner"]
    for f in fillers:
        if len(tags) == 13:
            break
        if f not in tags and len(f) <= 20:
            tags.append(f)

    # ----- DESCRIPTION -----
    description = f"""{theme.display_name} {planner_display_name} — printable PDF, instant download. Print at home on US Letter or A4; no shipping, no waiting.

WHAT YOU GET
- 1 high-resolution PDF ({page_count} page{"s" if page_count != 1 else ""})
- Print as many times as you like, for personal use
- Designed for 8.5x11" US Letter (scales cleanly to A4)

HOW IT WORKS
1. Purchase and download from your Etsy account → Purchases page
2. Open the PDF in any reader (Adobe Acrobat, Preview, browser)
3. Print at home, at a print shop, or use a tablet (GoodNotes / Notability)

PERFECT FOR
- Anyone who wants a {", ".join(theme.mood_words[:3])} look
- New month or new week resets
- Pairing with the rest of the {theme.display_name} collection

NOTES
- This is a DIGITAL product. No physical item will be shipped.
- Colors may print slightly differently depending on your printer settings.
- For personal use only — please do not resell or redistribute.

Questions? Message me anytime — I usually reply within a few hours.
"""

    return Listing(
        title=title,
        tags=tags[:13],
        description=description.strip(),
        materials=["PDF file", "printable", "digital download",
                   "instant download", "US Letter"],
        suggested_price_usd=_suggest_price(planner_display_name, page_count),
        sku=sku,
    )


def _suggest_price(display_name: str, pages: int) -> float:
    # Etsy printable planners in 2024-2026: $3-15 range.
    # Single-page templates: $3-6. Multi-page bundles: $8-15.
    base = 4.50
    if "workbook" in display_name.lower():
        base = 6.00
    if pages >= 5:
        base += 3.00
    if pages >= 10:
        base += 4.00
    return round(base, 2)


def render_listing_text(l: Listing) -> str:
    return f"""=== ETSY LISTING ({l.sku}) ===

TITLE  ({len(l.title)}/140)
{l.title}

TAGS  ({len(l.tags)}/13)
{chr(10).join("  - " + t for t in l.tags)}

MATERIALS
{chr(10).join("  - " + m for m in l.materials)}

SUGGESTED PRICE
${l.suggested_price_usd:.2f}

DESCRIPTION
{l.description}
"""
