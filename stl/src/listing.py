"""Generate platform-specific listing copy for an STL via Claude."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List

from anthropic import Anthropic

MODEL = "claude-opus-4-7"


def _strip(t: str) -> str:
    t = t.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    return t.strip()


@dataclass
class ListingPack:
    title: str
    short_desc: str          # one-line tagline for thumbnails
    cults3d: Dict             # platform-specific fields below
    makerworld: Dict
    printables: Dict
    thingiverse: Dict
    etsy_digital: Dict
    patreon_post: str
    recommended_print_settings: Dict
    suggested_tags: List[str]


SYSTEM = """You are a 3D printing community veteran and listing copywriter.
You write listing copy for STL files that ranks in search on Cults3D, MakerWorld,
Printables, Thingiverse, and Etsy, AND converts browsers into downloads.

Voice: enthusiastic but not salesy, technically accurate, written by a maker for
makers. Mention real print settings (layer height, supports, orientation).

Output strict JSON only. Schema:

{
  "title": "max 60 chars, search-keyword forward",
  "short_desc": "one sentence, under 100 chars",
  "cults3d": {
    "title": "...",
    "description": "300-700 chars markdown, full features + print settings + license note",
    "tags": ["tag1", ...8-12 tags lowercase]
  },
  "makerworld": {
    "title": "...",
    "description": "200-500 chars, focuses on Bambu print profile compatibility",
    "tags": ["tag1", ...6-10 tags]
  },
  "printables": {
    "title": "...",
    "description": "300-600 chars, friendly tone for Prusa community",
    "tags": ["tag1", ...6-10 tags]
  },
  "thingiverse": {
    "title": "...",
    "description": "200-500 chars",
    "tags": ["tag1", ...6-10 tags]
  },
  "etsy_digital": {
    "title": "max 140 chars, keyword stuffed but natural (Etsy SEO)",
    "description": "500-1200 chars, sells the lifestyle/use-case not the technical specs (Etsy buyers may not own a printer; emphasize 'have it printed for you' service if applicable)",
    "tags": ["tag1", ...exactly 13 tags, max 20 chars each]
  },
  "patreon_post": "300-500 chars announcing the new file to your patrons, casual",
  "recommended_print_settings": {
    "layer_height_mm": 0.2,
    "infill_pct": 15,
    "supports": "none | tree | normal",
    "orientation_note": "1 line",
    "material": "PLA | PETG | etc",
    "notes": "2-3 sentence print tips"
  },
  "suggested_tags": ["broad tags useful across platforms, 8-12 lowercase"]
}

Rules:
- NEVER claim it's "AI-designed" or anything similar.
- License: assume "Personal use only, no resale or distribution" unless the user
  says otherwise.
- If the design is functional (a tool, holder, mount), emphasize the problem it
  solves. If decorative, emphasize the visual style and use-case.
- Etsy buyers especially: many will pay for a printed-and-shipped version, so
  the Etsy description should mention that option if the user offers print
  services."""


def generate_listing(
    design_name: str,
    user_description: str,
    bbox_mm: tuple[float, float, float],
    volume_cm3: float,
    print_time_hours: float,
    filament_weight_g: float,
    suggested_material: str = "PLA",
    offers_print_service: bool = True,
    license_note: str = "Personal use only, no resale or distribution",
) -> ListingPack:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    w, d, h = bbox_mm
    user = f"""Design name (working title):
{design_name}

What it is (from the designer):
{user_description}

Technical specs:
- Bounding box:       {w:.0f} x {d:.0f} x {h:.0f} mm
- Solid volume:       {volume_cm3:.1f} cm³
- Est. print time:    {print_time_hours:.1f} hours
- Est. filament:      {filament_weight_g:.0f} g
- Suggested material: {suggested_material}

Designer offers print-and-ship service: {"yes" if offers_print_service else "no"}
License: {license_note}

Generate the listing pack now. JSON only."""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=5000,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    data = json.loads(_strip(resp.content[0].text))

    return ListingPack(
        title=data["title"],
        short_desc=data["short_desc"],
        cults3d=data["cults3d"],
        makerworld=data["makerworld"],
        printables=data["printables"],
        thingiverse=data["thingiverse"],
        etsy_digital=data["etsy_digital"],
        patreon_post=data["patreon_post"],
        recommended_print_settings=data["recommended_print_settings"],
        suggested_tags=data.get("suggested_tags", []),
    )


def write_platform_files(pack: ListingPack, out_dir: Path, suggested_prices: Dict[str, float]) -> None:
    """Persist one .txt per platform with the copy ready to paste."""
    from pathlib import Path
    out_dir.mkdir(parents=True, exist_ok=True)

    def fmt_tags(tags: list) -> str:
        return ", ".join(tags)

    def write(name: str, header: str, data: dict, price: float | None) -> None:
        lines = [
            f"=== {header} ===",
            "",
            f"TITLE  (paste into the listing's title field):",
            data["title"],
            "",
            f"DESCRIPTION  (paste into the listing's description field):",
            data["description"],
            "",
            f"TAGS:",
            fmt_tags(data.get("tags", [])),
        ]
        if price is not None and price > 0:
            lines += ["", f"SUGGESTED PRICE: ${price:.2f}"]
        elif price == 0:
            lines += ["", "PRICING: free (platform pays via engagement points/rewards program)"]
        (out_dir / f"listing_{name}.txt").write_text("\n".join(lines))

    write("cults3d",     "Cults3D listing",     pack.cults3d,     suggested_prices.get("cults3d"))
    write("makerworld",  "MakerWorld (Bambu) listing", pack.makerworld,  suggested_prices.get("makerworld"))
    write("printables",  "Printables (Prusa) listing", pack.printables,  suggested_prices.get("printables"))
    write("thingiverse", "Thingiverse listing", pack.thingiverse, suggested_prices.get("thingiverse"))
    write("etsy",        "Etsy digital listing", pack.etsy_digital, suggested_prices.get("etsy"))

    # Patreon post.
    (out_dir / "patreon_post.txt").write_text(
        "=== Patreon post ===\n\n" + pack.patreon_post +
        "\n\n---\nUpload the iso render as the post image."
    )

    # Print settings.
    s = pack.recommended_print_settings
    settings_lines = [
        "=== Recommended Print Settings ===",
        "",
        f"Layer height:   {s.get('layer_height_mm', 0.2)} mm",
        f"Infill:         {s.get('infill_pct', 15)}%",
        f"Supports:       {s.get('supports', 'none')}",
        f"Orientation:    {s.get('orientation_note', 'as oriented in the file')}",
        f"Material:       {s.get('material', 'PLA')}",
        "",
        "Print notes:",
        s.get("notes", ""),
    ]
    (out_dir / "print_settings.txt").write_text("\n".join(settings_lines))
