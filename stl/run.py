#!/usr/bin/env python3
"""House of Hudson — STL listing & quote pipeline.

For every design folder in  stl/input/  this tool produces a complete listing
package in  stl/output/<date>/<design-name>/ :

  render_iso.png, render_front.png, render_top.png
  listing_cults3d.txt, listing_makerworld.txt, listing_printables.txt,
  listing_thingiverse.txt, listing_etsy.txt, patreon_post.txt
  print_settings.txt
  stl_pricing.txt
  quote.pdf  (if a customer for print-and-ship is specified)
  analysis.txt
"""
from __future__ import annotations

import datetime as dt
import re
import sys
import traceback
from pathlib import Path

import yaml
from dotenv import load_dotenv

STL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = STL_ROOT.parent
sys.path.insert(0, str(STL_ROOT))

from src.analyze import analyze_stl, format_summary
from src.listing import generate_listing, write_platform_files
from src.pricing import PricingConfig, quote_print, suggest_stl_price
from src.quote_pdf import build_quote_pdf
from src.render_views import render_all_views


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60]


def _check_env() -> None:
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n[!] ANTHROPIC_API_KEY not set. Open .env and paste your key.")
        sys.exit(1)


def _find_stls(design_dir: Path) -> list[Path]:
    """Return STL files in a design folder, case-insensitive."""
    if not design_dir.is_dir():
        return []
    return sorted(
        p for p in design_dir.iterdir()
        if p.is_file() and p.suffix.lower() in (".stl", ".3mf", ".obj")
    )


def _read_description(design_dir: Path) -> str:
    desc_path = design_dir / "description.txt"
    if desc_path.exists():
        return desc_path.read_text().strip()
    customer_path = design_dir / "customer.txt"
    if customer_path.exists():
        return customer_path.read_text().strip()
    return ""


def _read_customer(design_dir: Path) -> dict | None:
    """Optional customer.yaml = {name, email, notes} → indicates a print-and-ship quote is wanted."""
    p = design_dir / "customer.yaml"
    if not p.exists():
        return None
    try:
        return yaml.safe_load(p.read_text())
    except Exception:
        return None


def _process_design(design_dir: Path, out_dir: Path, config: dict) -> bool:
    stls = _find_stls(design_dir)
    if not stls:
        print(f"  [skip] No STL/3MF/OBJ files in {design_dir}")
        return False

    design_name = design_dir.name
    description = _read_description(design_dir)
    if not description:
        # Fall back to using the folder name as the description hint.
        description = f"A design called '{design_name}'."

    customer = _read_customer(design_dir)
    target_dir = out_dir / design_name
    target_dir.mkdir(parents=True, exist_ok=True)

    material = config.get("default_material", "PLA")
    infill = int(config.get("default_infill_pct", 20))
    do = set(config.get("generate", []))

    # Use the first STL as the primary file; if multiple are in the folder, they
    # belong to the same design and we'll just analyze the largest.
    primary = max(stls, key=lambda p: p.stat().st_size)

    print(f"  [analyze] {primary.name}")
    a = analyze_stl(primary, material=material, infill_pct=infill)
    (target_dir / "analysis.txt").write_text(format_summary(a))

    pricing_cfg = PricingConfig(
        filament_cost_per_kg=float(config["pricing"]["filament_cost_per_kg"]),
        machine_rate_per_hour=float(config["pricing"]["machine_rate_per_hour"]),
        labor_rate_per_hour=float(config["pricing"]["labor_rate_per_hour"]),
        setup_minutes=int(config["pricing"]["setup_minutes"]),
        markup_pct=int(config["pricing"]["markup_pct"]),
        currency_symbol=config.get("currency_symbol", "$"),
    )

    if "stl_pricing" in do:
        prices = suggest_stl_price(a.bbox_mm, a.triangle_count, cfg=pricing_cfg)
        lines = [
            "=== Suggested STL pricing (digital download / file sale) ===",
            "",
            f"Cults3D:                {pricing_cfg.currency_symbol}{prices['cults3d']:.2f}",
            f"Etsy (digital):         {pricing_cfg.currency_symbol}{prices['etsy']:.2f}",
            f"Direct site:            {pricing_cfg.currency_symbol}{prices['direct_site']:.2f}",
            f"Patreon (monthly tier): {pricing_cfg.currency_symbol}{prices['patreon_monthly_tier']:.0f}",
            f"MakerWorld:             free (Bambu pays you via engagement points)",
            f"Printables:             free (Prusa pays via club points)",
            f"Thingiverse:            free",
            "",
            "These are starting suggestions. Lower for simple/small designs, raise for intricate/large.",
        ]
        (target_dir / "stl_pricing.txt").write_text("\n".join(lines))
        print(f"  [pricing] STL prices written")
    else:
        prices = {}

    if "renders" in do:
        print(f"  [renders] generating {len(config.get('render_views', []))} views")
        try:
            render_all_views(
                primary,
                target_dir,
                style=config.get("render_style", "studio_white"),
                views=config.get("render_views", ["iso", "front", "top"]),
            )
        except Exception as e:
            print(f"  [!] Render failed: {e}")
            traceback.print_exc()

    if "listings" in do:
        print(f"  [listing] generating cross-platform copy via Claude")
        try:
            pack = generate_listing(
                design_name=design_name,
                user_description=description,
                bbox_mm=a.bbox_mm,
                volume_cm3=a.volume_cm3,
                print_time_hours=a.print_time_hours,
                filament_weight_g=a.filament_weight_g,
                suggested_material=material,
                offers_print_service=bool(config.get("offers_print_service", True)),
                license_note=config.get("license_note", "Personal use only"),
            )
            # Prepare a price lookup keyed the way listing writer expects.
            listing_prices = {
                "cults3d":     prices.get("cults3d", 0),
                "makerworld":  prices.get("makerworld", 0),
                "printables":  prices.get("printables", 0),
                "thingiverse": prices.get("thingiverse", 0),
                "etsy":        prices.get("etsy", 0),
            }
            write_platform_files(pack, target_dir, listing_prices)
        except Exception as e:
            print(f"  [!] Listing generation failed: {e}")
            traceback.print_exc()

    if "print_quote" in do and customer:
        print(f"  [quote] generating customer quote PDF for {customer.get('name', 'customer')}")
        try:
            q = quote_print(a.filament_weight_g, a.print_time_hours, cfg=pricing_cfg)
            build_quote_pdf(
                out_path=target_dir / "quote.pdf",
                business_name=config["business_name"],
                business_tagline=config["business_tagline"],
                business_contact=config["business_contact"],
                customer_name=customer.get("name", ""),
                job_name=design_name,
                job_description=customer.get("notes", description),
                bbox_mm=a.bbox_mm,
                print_time_hours=a.print_time_hours,
                filament_weight_g=a.filament_weight_g,
                material=material,
                quote_total=q.suggested_round,
                breakdown=q.breakdown,
                currency=pricing_cfg.currency_symbol,
            )
        except Exception as e:
            print(f"  [!] Quote PDF failed: {e}")
            traceback.print_exc()

    print(f"  [done] {target_dir}/")
    return True


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    _check_env()

    cfg = yaml.safe_load((STL_ROOT / "config.yaml").read_text())

    today = dt.date.today().isoformat()
    out_dir = STL_ROOT / "output" / today
    out_dir.mkdir(parents=True, exist_ok=True)

    input_dir = STL_ROOT / "input"
    designs = [d for d in input_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if not designs:
        print(f"\n[!] No design folders found in {input_dir}")
        print(f"    Create  stl/input/<design-name>/  and drop an STL file inside.")
        print(f"    Optionally add a description.txt describing what it is.")
        print(f"    For a customer quote, add customer.yaml with name/email/notes.")
        return 1

    print(f"\n=== House of Hudson — STL Pipeline ===")
    print(f"Designs found:  {len(designs)}")
    print(f"Output:         {out_dir}")
    print()

    successes = 0
    failures = 0
    for d in sorted(designs):
        print(f"\n>> {d.name}")
        try:
            if _process_design(d, out_dir, cfg):
                successes += 1
            else:
                failures += 1
        except Exception as e:
            print(f"  [!] Unhandled error: {e}")
            traceback.print_exc()
            failures += 1

    print()
    print(f"=== Done: {successes} successful, {failures} skipped/failed ===")
    print(f"Output: {out_dir}")
    print()
    print("Next steps:")
    print("  - Open each design folder and review the renders")
    print("  - Open listing_*.txt files, copy/paste into each platform")
    print("  - Upload the STL + renders to Cults3D / MakerWorld / Printables / Thingiverse / Etsy")
    print("  - Post the Patreon announcement")
    print("  - If a quote.pdf was generated, send it to the customer")
    return 0 if successes > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
