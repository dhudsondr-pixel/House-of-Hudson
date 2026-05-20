"""Batch wedding-stationery generator."""

from dataclasses import dataclass
from pathlib import Path

from reportlab.pdfgen import canvas as pdfcanvas

from . import mockups
from .cards import CARD_TYPES
from .listings import build_listing, render_listing_text
from .pdf_engine import INCH, SIZES
from .themes import THEMES, all_themes


@dataclass
class ProductSpec:
    card_slug: str
    theme_slug: str

    def sku(self) -> str:
        return f"{self.card_slug}__{self.theme_slug}"


def all_combinations() -> list[ProductSpec]:
    return [
        ProductSpec(card_slug=c, theme_slug=t.slug)
        for c in CARD_TYPES
        for t in all_themes()
    ]


def build_one(spec: ProductSpec, root: Path) -> Path:
    card_def = CARD_TYPES[spec.card_slug]
    theme = THEMES[spec.theme_slug]
    sku = spec.sku()

    folder = root / sku
    folder.mkdir(parents=True, exist_ok=True)

    size = SIZES[card_def["size"]]

    # 1. The customer-facing fillable PDF. Files are prefixed with the SKU so
    # they stay distinguishable when downloaded from several folders at once.
    pdf_path = folder / f"{sku}__product.pdf"
    c = pdfcanvas.Canvas(str(pdf_path), pagesize=size.pts)
    c.setTitle(f"{theme.display_name} {card_def['display_name']}")
    card_def["build"](c, theme, mode="fillable")
    c.save()

    # 2. A short-lived preview PDF (placeholders baked as static text) used
    # only to generate the listing mockup image.
    preview_path = folder / "_preview.pdf"
    c = pdfcanvas.Canvas(str(preview_path), pagesize=size.pts)
    card_def["build"](c, theme, mode="preview")
    c.save()

    # 3. Mockups
    mockups.hero(theme, card_def["display_name"],
                 str(folder / f"{sku}__image-1-hero.png"))
    mockups.card_on_background(theme, str(preview_path),
                               str(folder / f"{sku}__image-2-card.png"))
    mockups.feature_card(theme, card_def["display_name"],
                         str(folder / f"{sku}__image-3-features.png"))

    # Clean up the preview PDF — buyers should never see it.
    preview_path.unlink()

    # 3. Listing
    listing = build_listing(
        card_display_name=card_def["display_name"],
        card_keywords=card_def["keywords"],
        card_size_label=card_def["size"],
        theme=theme,
        sku=sku,
    )
    (folder / f"{sku}__listing.txt").write_text(render_listing_text(listing))

    return folder
