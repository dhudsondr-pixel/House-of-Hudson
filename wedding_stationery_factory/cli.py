"""CLI for the wedding stationery factory."""

import argparse
import sys
from pathlib import Path

from .cards import CARD_TYPES
from .factory import all_combinations, build_one, ProductSpec
from .themes import THEMES


def print_banner() -> None:
    print()
    print("=" * 60)
    print("  ETSY WEDDING STATIONERY FACTORY")
    print("=" * 60)
    print()
    print(f"  Card types:    {len(CARD_TYPES)}")
    print(f"  Themes:        {len(THEMES)}")
    print(f"  Combinations:  {len(CARD_TYPES) * len(THEMES)} unique listings")
    print()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="wedding_stationery_factory")
    ap.add_argument("--count", type=int, default=None)
    ap.add_argument("--output", default="output-wedding")
    ap.add_argument("--only-card", choices=list(CARD_TYPES))
    ap.add_argument("--only-theme", choices=list(THEMES))
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv if argv is not None else sys.argv[1:])

    if args.list:
        print_banner()
        print("CARD TYPES")
        for slug, c in CARD_TYPES.items():
            print(f"  - {slug:20s} {c['display_name']:24s} ({c['size']}\")")
        print()
        print("THEMES")
        for slug, t in THEMES.items():
            print(f"  - {slug:24s} {t.display_name}")
        return 0

    print_banner()
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)

    specs = all_combinations()
    if args.only_card:
        specs = [s for s in specs if s.card_slug == args.only_card]
    if args.only_theme:
        specs = [s for s in specs if s.theme_slug == args.only_theme]
    if args.count is not None:
        specs = specs[: args.count]

    print(f"Building {len(specs)} listings into '{root}/' ...\n")
    for i, spec in enumerate(specs, 1):
        folder = build_one(spec, root)
        print(f"  [{i:2d}/{len(specs)}]  {folder.name}")

    print()
    print("=" * 60)
    print("  DONE.")
    print("=" * 60)
    print(f"\nYour listings are in:  {root.resolve()}")
    print("\nNext steps:")
    print("  1. Open the 'output-wedding' folder.")
    print("  2. Each subfolder is one Etsy listing. Every file is prefixed")
    print("     with the listing name so they stay unique if you download")
    print("     several at once:")
    print("       ...__product.pdf          <- fillable PDF the buyer downloads")
    print("       ...__image-1-hero.png     <- Etsy listing image 1 (cover)")
    print("       ...__image-2-card.png     <- Etsy listing image 2 (preview)")
    print("       ...__image-3-features.png <- Etsy listing image 3 (features)")
    print("       ...__listing.txt          <- title, tags, description, price")
    print("  3. On Etsy: Create New Listing -> upload the 3 PNGs, set type to")
    print("     'Digital file', upload product.pdf, paste in title/tags/desc.")
    print("  4. Important: in the description, mention 'edit in Adobe Reader'")
    print("     so buyers know it's fillable, not Canva-editable.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
