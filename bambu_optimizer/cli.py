"""Command-line entry point.

Examples
--------
    # Interactive wizard
    python -m bambu_optimizer

    # Direct
    python -m bambu_optimizer --printer H2D --material PA-CF \
        --quality fine --purpose mechanical --overhangs

    # Compare every printer for the same job
    python -m bambu_optimizer --material PETG --purpose functional --compare-all
"""

import argparse
import sys

from .materials import MATERIALS
from .optimizer import PrintIntent, recommend
from .printers import PRINTERS
from .render import as_json, as_studio_overrides, as_text


def _bool(prompt: str, default: bool = False) -> bool:
    suffix = " [Y/n]" if default else " [y/N]"
    raw = input(prompt + suffix + " ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes", "1", "true")


def _choice(prompt: str, options, default: str) -> str:
    options = list(options)
    print(prompt)
    for i, opt in enumerate(options, 1):
        marker = " (default)" if opt == default else ""
        print(f"  {i}. {opt}{marker}")
    raw = input("> ").strip()
    if not raw:
        return default
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw) - 1]
    if raw.upper() in [o.upper() for o in options]:
        return next(o for o in options if o.upper() == raw.upper())
    print(f"  (unrecognized, using default '{default}')")
    return default


def interactive() -> tuple[str, str, float | None, PrintIntent]:
    print("Bambu Lab print settings optimizer\n")
    printer = _choice("Which printer?", PRINTERS, "H2D")
    material = _choice("Which filament?", MATERIALS, "PLA")
    nozzles = PRINTERS[printer].nozzle_sizes_mm
    nozzle_str = _choice(
        f"Nozzle size (mm)?",
        [str(n) for n in nozzles],
        str(PRINTERS[printer].default_nozzle_mm),
    )
    nozzle = float(nozzle_str)

    quality = _choice(
        "Quality target?",
        ["draft", "standard", "fine", "ultrafine"],
        "standard",
    )
    purpose = _choice(
        "Part purpose?",
        ["visual", "functional", "mechanical", "miniature", "prototype"],
        "functional",
    )

    intent = PrintIntent(
        quality=quality,                                  # type: ignore[arg-type]
        purpose=purpose,                                  # type: ignore[arg-type]
        has_overhangs=_bool("Has overhangs >55deg?"),
        has_bridges=_bool("Has bridges?"),
        tall_and_narrow=_bool("Is the part tall and narrow (H:W > 3:1)?"),
        fine_detail=_bool("Has fine detail/text/embossing?"),
        watertight=_bool("Must be watertight?"),
        transparent=_bool("Want transparency?"),
        annealed_after=_bool("Will you anneal afterward?"),
        outdoor_use=_bool("Outdoor / UV exposure?"),
    )
    return printer, material, nozzle, intent


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="bambu_optimizer",
        description="Recommend Bambu Studio settings for a given printer/material/intent.",
    )
    p.add_argument("--printer", choices=list(PRINTERS))
    p.add_argument("--material", choices=list(MATERIALS))
    p.add_argument("--nozzle", type=float, help="Nozzle size in mm")
    p.add_argument("--quality", choices=["draft", "standard", "fine", "ultrafine"], default="standard")
    p.add_argument("--purpose", choices=["visual", "functional", "mechanical", "miniature", "prototype"],
                   default="functional")
    p.add_argument("--overhangs", action="store_true")
    p.add_argument("--bridges", action="store_true")
    p.add_argument("--tall-narrow", action="store_true")
    p.add_argument("--fine-detail", action="store_true")
    p.add_argument("--watertight", action="store_true")
    p.add_argument("--transparent", action="store_true")
    p.add_argument("--annealed", action="store_true")
    p.add_argument("--outdoor", action="store_true")
    p.add_argument("--height", type=float, default=50.0)
    p.add_argument("--format", choices=["text", "json", "studio"], default="text")
    p.add_argument("--compare-all", action="store_true",
                   help="Print recommendations for every printer side by side.")
    return p.parse_args(argv)


def _format(r, fmt):
    if fmt == "json":
        return as_json(r)
    if fmt == "studio":
        return as_studio_overrides(r)
    return as_text(r)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.printer is None and args.material is None and not args.compare_all:
        printer, material, nozzle, intent = interactive()
        print()
        print(_format(recommend(printer, material, intent, nozzle), args.format))
        return 0

    if args.material is None:
        print("--material is required (or run with no args for the wizard).", file=sys.stderr)
        return 2

    intent = PrintIntent(
        quality=args.quality,
        purpose=args.purpose,
        has_overhangs=args.overhangs,
        has_bridges=args.bridges,
        tall_and_narrow=args.tall_narrow,
        fine_detail=args.fine_detail,
        watertight=args.watertight,
        transparent=args.transparent,
        annealed_after=args.annealed,
        outdoor_use=args.outdoor,
        estimated_part_height_mm=args.height,
    )

    if args.compare_all:
        for name in PRINTERS:
            try:
                r = recommend(name, args.material, intent, args.nozzle)
            except ValueError as e:
                print(f"--- {name}: skipped ({e}) ---\n")
                continue
            print(_format(r, args.format))
            print()
        return 0

    if args.printer is None:
        print("--printer is required (or use --compare-all).", file=sys.stderr)
        return 2

    print(_format(recommend(args.printer, args.material, intent, args.nozzle), args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
