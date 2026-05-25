#!/usr/bin/env python3
"""House of Hudson — daily social content factory.

Run with:  python social/run.py

Reads `social/config.yaml` and produces a folder-per-platform tree of
ready-to-upload posts in `social/output/<today>/`.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
import traceback
from pathlib import Path

import yaml
from dotenv import load_dotenv

SOCIAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SOCIAL_ROOT.parent
sys.path.insert(0, str(SOCIAL_ROOT))

from src import instagram, pinterest, textposts
from src.render import save_png
from src.strategist import generate_plan


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:50]


def _check_env() -> None:
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n[!] ANTHROPIC_API_KEY not set.")
        print("    Copy .env.example to .env and paste your key.")
        sys.exit(1)


def _resolve_book_context(config: dict) -> str:
    book_dir = (config.get("featured_book_dir") or "").strip()
    if book_dir:
        meta_path = REPO_ROOT / book_dir / "metadata.txt"
        if meta_path.exists():
            return meta_path.read_text()
    return config.get("featured_book_context", "").strip()


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    _check_env()

    config = yaml.safe_load((SOCIAL_ROOT / "config.yaml").read_text())

    brand = config["brand_name"]
    niche = config["niche"]
    audience = config["audience"]
    tagline = config.get("tagline", "")
    link = config.get("link_in_bio", "")
    platforms = set(config.get("platforms", []))
    qty = config.get("quantities", {})
    palettes = config.get("allowed_palettes") or None

    book_context = _resolve_book_context(config)
    if not book_context:
        book_context = f"(no specific book focus — promote the brand and niche generally)"

    today = dt.date.today().isoformat()
    out_dir = SOCIAL_ROOT / "output" / today
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== House of Hudson — Social Content Factory ===")
    print(f"Brand:     {brand}")
    print(f"Niche:     {niche}")
    print(f"Platforms: {', '.join(sorted(platforms))}")
    print(f"Output:    {out_dir}")
    print()

    print("[1/3] Generating cross-platform content plan via Claude...")
    try:
        plan = generate_plan(
            brand_name=brand,
            niche=niche,
            audience=audience,
            tagline=tagline,
            book_context=book_context,
            n_pinterest=qty.get("pinterest_pins", 5) if "pinterest" in platforms else 0,
            n_ig_quotes=qty.get("instagram_quotes", 1) if "instagram" in platforms else 0,
            n_ig_carousels=qty.get("instagram_carousels", 1) if "instagram" in platforms else 0,
            n_threads=qty.get("twitter_threads", 1) if "twitter" in platforms else 0,
            n_tiktok=qty.get("tiktok_scripts", 1) if "tiktok" in platforms else 0,
        )
    except Exception as e:
        print(f"[!] Content plan generation failed: {e}")
        traceback.print_exc()
        return 1

    counts = {
        "pinterest": len(plan.get("pinterest_pins", [])),
        "instagram_quotes": len(plan.get("instagram_quotes", [])),
        "instagram_carousels": len(plan.get("instagram_carousels", [])),
        "twitter": len(plan.get("twitter_threads", [])),
        "tiktok": len(plan.get("tiktok_scripts", [])),
    }
    print(f"      Plan: {counts}")

    print("\n[2/3] Rendering images and writing captions...")

    successes = 0
    failures = 0

    # ---- Pinterest ----
    if "pinterest" in platforms:
        pin_dir = out_dir / "pinterest"
        for i, p in enumerate(plan.get("pinterest_pins", []), 1):
            try:
                seed = f"{brand}|{p.get('hook','')}|{i}"
                img = pinterest.build_pin(
                    hook=p["hook"],
                    subhead=p.get("subhead", ""),
                    style=p.get("style", "bold"),
                    brand=brand,
                    seed=seed,
                    palette_keys=palettes,
                )
                slug = _slug(p["hook"])
                img_path = pin_dir / f"{i:02d}_{slug}.png"
                save_png(img, img_path)
                pinterest.write_caption(
                    pin_dir / f"{i:02d}_{slug}.txt",
                    hook=p["hook"],
                    description=p.get("description", ""),
                    hashtags=p.get("hashtags", []),
                    link_in_bio=link,
                    title_field=p.get("hook"),
                )
                successes += 1
                print(f"      [pinterest] {img_path.name}")
            except Exception as e:
                failures += 1
                print(f"      [!] Pinterest pin {i} failed: {e}")

    # ---- Instagram quotes ----
    if "instagram" in platforms:
        ig_dir = out_dir / "instagram"
        for i, q in enumerate(plan.get("instagram_quotes", []), 1):
            try:
                seed = f"{brand}|{q.get('quote','')}|q{i}"
                img = instagram.build_quote(q["quote"], brand, seed, palette_keys=palettes)
                slug = _slug(q["quote"])
                img_path = ig_dir / f"quote_{i:02d}_{slug}.png"
                save_png(img, img_path)
                instagram.write_caption(
                    ig_dir / f"quote_{i:02d}_{slug}.txt",
                    caption=q.get("caption", q["quote"]),
                    hashtags=q.get("hashtags", []),
                )
                successes += 1
                print(f"      [instagram] {img_path.name}")
            except Exception as e:
                failures += 1
                print(f"      [!] IG quote {i} failed: {e}")

        # ---- Instagram carousels ----
        for i, car in enumerate(plan.get("instagram_carousels", []), 1):
            try:
                seed = f"{brand}|{car.get('hook','')}|c{i}"
                imgs = instagram.build_carousel(
                    hook=car["hook"],
                    slides=car.get("slides", []),
                    brand=brand,
                    seed=seed,
                    palette_keys=palettes,
                )
                slug = _slug(car["hook"])
                car_dir = ig_dir / f"carousel_{i:02d}_{slug}"
                car_dir.mkdir(parents=True, exist_ok=True)
                for j, img in enumerate(imgs, 1):
                    save_png(img, car_dir / f"slide_{j}.png")
                instagram.write_caption(
                    car_dir / "caption.txt",
                    caption=car.get("caption", ""),
                    hashtags=car.get("hashtags", []),
                )
                successes += 1
                print(f"      [instagram] carousel_{i:02d}_{slug}/ ({len(imgs)} slides)")
            except Exception as e:
                failures += 1
                print(f"      [!] IG carousel {i} failed: {e}")

    # ---- Twitter ----
    if "twitter" in platforms:
        tw_dir = out_dir / "twitter"
        for i, th in enumerate(plan.get("twitter_threads", []), 1):
            try:
                textposts.write_thread(
                    tw_dir / f"thread_{i:02d}.txt",
                    tweets=th.get("tweets", []),
                    topic=th.get("topic", ""),
                )
                successes += 1
                print(f"      [twitter] thread_{i:02d}.txt ({len(th.get('tweets', []))} tweets)")
            except Exception as e:
                failures += 1
                print(f"      [!] Twitter thread {i} failed: {e}")

    # ---- TikTok scripts ----
    if "tiktok" in platforms:
        tt_dir = out_dir / "tiktok"
        for i, sc in enumerate(plan.get("tiktok_scripts", []), 1):
            try:
                textposts.write_tiktok_script(
                    tt_dir / f"script_{i:02d}.txt",
                    hook=sc.get("hook", ""),
                    narration=sc.get("narration", ""),
                    captions=sc.get("captions", []),
                    visual_keywords=sc.get("visual_keywords", []),
                    cta=sc.get("cta", ""),
                )
                successes += 1
                print(f"      [tiktok] script_{i:02d}.txt")
            except Exception as e:
                failures += 1
                print(f"      [!] TikTok script {i} failed: {e}")

    print(f"\n[3/3] Done. {successes} posts ready, {failures} failures.")
    print(f"      Output folder: {out_dir}")
    print()
    print("Upload workflow:")
    print("  Pinterest:   https://business.pinterest.com → 'Schedule pin' (free, up to 100 scheduled)")
    print("  Instagram:   https://business.facebook.com → Planner → upload images & schedule")
    print("  Twitter/X:   post tweets manually (or use https://typefully.com)")
    print("  TikTok:      record video using script, upload at https://www.tiktok.com/upload")
    print()
    print("Recommended cadence:")
    print("  - Pinterest: 5-10 pins per day, scheduled across the day")
    print("  - Instagram: 1 post in the morning, 1 in the evening")
    print("  - Twitter:   1 thread + 2-3 standalone tweets per day")
    print("  - TikTok:    1 video per day (more if you can sustain)")
    return 0 if successes > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
