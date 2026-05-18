"""Batch product generator.

For each (planner_type x theme) combination, produces:
  output/<sku>/
    product.pdf          <- the digital file customers receive
    image-1-hero.png     <- Etsy listing image 1
    image-2-preview.png  <- Etsy listing image 2
    image-3-card.png     <- Etsy listing image 3
    listing.txt          <- title / tags / description / price
"""

from dataclasses import dataclass
from pathlib import Path

from . import mockups
from .listings import build_listing, render_listing_text
from .pdf_engine import new_doc
from .planners import PLANNER_TYPES
from .themes import THEMES, all_themes


@dataclass
class ProductSpec:
    planner_slug: str
    theme_slug: str

    def sku(self) -> str:
        return f"{self.planner_slug}__{self.theme_slug}"


def all_combinations() -> list[ProductSpec]:
    return [
        ProductSpec(planner_slug=p, theme_slug=t.slug)
        for p in PLANNER_TYPES
        for t in all_themes()
    ]


def build_one(spec: ProductSpec, root: Path) -> Path:
    planner = PLANNER_TYPES[spec.planner_slug]
    theme = THEMES[spec.theme_slug]
    sku = spec.sku()

    folder = root / sku
    folder.mkdir(parents=True, exist_ok=True)

    # 1. PDF
    pdf_path = folder / "product.pdf"
    c = new_doc(str(pdf_path))
    planner["build"](c, theme)
    c.save()

    # 2. Mockup images
    mockups.hero(theme, planner["display_name"], str(folder / "image-1-hero.png"))
    mockups.preview(theme, planner["display_name"], str(folder / "image-2-preview.png"))
    mockups.card(
        theme,
        planner["display_name"],
        bullets=[
            "Print-ready PDF",
            "US Letter & A4 compatible",
            "Instant download",
            "Use again and again",
            f"{theme.display_name} aesthetic",
        ],
        out_path=str(folder / "image-3-card.png"),
    )

    # 3. Listing copy
    listing = build_listing(
        planner_display_name=planner["display_name"],
        planner_keywords=planner["keywords"],
        theme=theme,
        sku=sku,
        page_count=1,
    )
    (folder / "listing.txt").write_text(render_listing_text(listing))

    return folder


def build_batch(count: int | None, root: Path) -> list[Path]:
    specs = all_combinations()
    if count is not None:
        specs = specs[:count]
    return [build_one(s, root) for s in specs]
