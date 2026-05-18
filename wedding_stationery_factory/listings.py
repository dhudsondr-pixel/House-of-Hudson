"""Etsy listing copy for wedding stationery.

Wedding buyers search differently from planner buyers:
- They search by aesthetic ("sage green wedding invitation")
- They search by venue type ("rustic", "garden", "modern")
- They search by editability ("editable invitation", "instant download invitation")

The title formula that ranks: [Style] + [Card Type] + Template + [Format] + Edit/Print info.
"""

from dataclasses import dataclass

from .themes import WeddingTheme


@dataclass
class WeddingListing:
    title: str
    tags: list[str]
    description: str
    materials: list[str]
    suggested_price_usd: float
    sku: str


def _truncate(s: str, limit: int) -> str:
    return s if len(s) <= limit else s[:limit].rsplit(" ", 1)[0]


def _dedupe_tags(items):
    seen, out = set(), []
    for x in items:
        k = x.lower().strip()
        if k in seen or not k:
            continue
        if len(k) > 20:
            continue
        seen.add(k)
        out.append(k)
    return out


def build_listing(
    card_display_name: str,
    card_keywords: tuple[str, ...],
    card_size_label: str,
    theme: WeddingTheme,
    sku: str,
) -> WeddingListing:
    primary = card_keywords[0]
    mood = theme.mood_words[0]

    raw_title = (
        f"{theme.display_name} {card_display_name} Template | "
        f"Editable {primary.title()} | "
        f"Printable PDF | Instant Download | {card_size_label}\""
    )
    title = _truncate(raw_title, 140)

    candidate_tags = [
        primary,
        f"{mood} wedding",
        f"editable {primary.split()[0]}" if " " in primary else "editable template",
        "wedding template",
        "printable wedding",
        "instant download",
        "wedding stationery",
        "wedding suite",
        "wedding printable",
        f"{mood} invitation",
        "fillable pdf",
        "wedding pdf",
        *card_keywords[1:],
        "wedding invite",
        "diy wedding",
        "wedding download",
    ]
    tags = _dedupe_tags(candidate_tags)[:13]

    description = f"""{theme.display_name} {card_display_name} — editable PDF template, instant download.

You type your names, date, and details directly into the PDF using free Adobe Acrobat Reader. No Canva account, no Corjl, no waiting. Then print at home or send to your favorite print shop.

WHAT YOU GET
- 1 editable PDF ({card_size_label}\" trim size, print-ready)
- Pre-built text fields you can type into (names, date, venue, etc.)
- Use Adobe Acrobat Reader (free download) to edit
- Print as many copies as you need, for your wedding only

HOW IT WORKS
1. Buy and download from your Etsy Purchases page (instant).
2. Open the PDF in Adobe Acrobat Reader (free at get.adobe.com/reader).
3. Click each text field, type your details, save.
4. Print at home on cardstock, or upload to a print shop (Vistaprint, Staples, Minted, your local shop).

PRINT-READY DETAILS
- Trim size: {card_size_label}"
- Format: PDF, 300 DPI, designed for cardstock
- For best results: print on 110-130lb cardstock; cut along the trim line.

PERFECT FOR
- Couples planning a {", ".join(theme.mood_words[:3])} wedding
- DIY brides and grooms who want a polished suite without the price tag
- Last-minute timelines (you can print same-day)

NOTES
- This is a DIGITAL product. No physical item ships.
- Personal use only — please do not resell the template or files.
- Colors may vary slightly depending on your printer and cardstock.
- Need a matching RSVP, details card, or menu in this design? They're in my shop.

Questions? Message me — I usually reply within a few hours.
"""

    return WeddingListing(
        title=title,
        tags=tags,
        description=description.strip(),
        materials=["PDF template", "editable", "printable",
                   "instant download", "digital download"],
        suggested_price_usd=_suggest_price(card_display_name),
        sku=sku,
    )


def _suggest_price(display_name: str) -> float:
    # Etsy market rates for editable PDF templates (2024-2026):
    # Invitations: $10-20.  Save the Date: $8-15.  RSVP/Details: $5-10.
    # Menu/Thank You: $7-12.
    name = display_name.lower()
    if "invitation" in name:
        return 14.00
    if "save" in name:
        return 9.00
    if "menu" in name:
        return 8.00
    if "thank" in name:
        return 7.00
    return 6.50  # rsvp, details


def render_listing_text(l: WeddingListing) -> str:
    return f"""=== ETSY WEDDING LISTING ({l.sku}) ===

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
