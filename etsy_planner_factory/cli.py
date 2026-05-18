"""Command-line entry point with friendly prompts for non-coders."""

import argparse
import sys
from pathlib import Path

from .factory import all_combinations, build_batch, build_one, ProductSpec
from .planners import PLANNER_TYPES
from .themes import THEMES


def print_banner() -> None:
    print()
    print("=" * 60)
    print("  ETSY PRINTABLE PLANNER FACTORY")
    print("=" * 60)
    print()
    print(f"  Planner types: {len(PLANNER_TYPES)}")
    print(f"  Themes:        {len(THEMES)}")
    print(f"  Combinations:  {len(PLANNER_TYPES) * len(THEMES)} unique listings possible")
    print()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="etsy_planner_factory")
    ap.add_argument("--count", type=int, default=None,
                    help="How many listings to generate (default: all 36).")
    ap.add_argument("--output", default="output",
                    help="Folder to write listings to (default: output/)")
    ap.add_argument("--only-planner", choices=list(PLANNER_TYPES),
                    help="Generate only one planner type across all themes.")
    ap.add_argument("--only-theme", choices=list(THEMES),
                    help="Generate only one theme across all planner types.")
    ap.add_argument("--list", action="store_true",
                    help="List planner types and themes, then exit.")
    args = ap.parse_args(argv if argv is not None else sys.argv[1:])

    if args.list:
        print_banner()
        print("PLANNER TYPES")
        for slug, p in PLANNER_TYPES.items():
            print(f"  - {slug:20s} {p['display_name']}")
        print()
        print("THEMES")
        for slug, t in THEMES.items():
            print(f"  - {slug:20s} {t.display_name}")
        return 0

    print_banner()

    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)

    specs = all_combinations()
    if args.only_planner:
        specs = [s for s in specs if s.planner_slug == args.only_planner]
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
    print("  1. Open the 'output' folder.")
    print("  2. For each subfolder, you'll find:")
    print("       product.pdf          <- the file your buyer downloads")
    print("       image-1-hero.png     <- first Etsy listing image")
    print("       image-2-preview.png  <- second image (sample page)")
    print("       image-3-card.png     <- third image (what's included)")
    print("       listing.txt          <- copy/paste for title, tags, description")
    print("  3. On Etsy: Create New Listing -> upload the 3 images and the PDF,")
    print("     then copy/paste the title, tags, and description from listing.txt.")
    print("  4. Upload 3-5 listings per day, every day, for one month.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
