#!/usr/bin/env python3
"""House of Hudson — KDP auto-publishing.

Run with:  python kdp/run.py

Generates a folder per book containing:
  - interior.pdf  (upload to KDP "Manuscript")
  - cover.pdf     (upload to KDP "Book Cover")
  - metadata.txt  (copy/paste fields into the KDP listing form)
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
import traceback
from pathlib import Path

import yaml
from dotenv import load_dotenv

KDP_ROOT = Path(__file__).resolve().parent
REPO_ROOT = KDP_ROOT.parent
sys.path.insert(0, str(KDP_ROOT))

from src import wordsearch as ws_gen
from src.covers import build_cover
from src.interiors import (
    build_lined_interior,
    build_prompt_journal_interior,
    build_tracker_interior,
    build_wordsearch_interior,
)
from src.metadata import (
    generate_metadata,
    generate_prompts,
    generate_wordsearch_themes,
)
from src.niches import brainstorm
from src.specs import estimate_royalty


def _slug(text: str) -> str:
    s = text.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60]


def _load_history(path: Path) -> list:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def _save_history(path: Path, items: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, indent=2))


def _check_env() -> None:
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n[!] ANTHROPIC_API_KEY not set.")
        print("    Copy .env.example to .env and paste your key.")
        print("    Get a key at: https://console.anthropic.com/")
        sys.exit(1)


def _write_metadata_file(path: Path, meta, book_type: str, niche_obj: dict,
                        page_count: int, trim: str, paper: str, author_name: str,
                        list_price: float, royalty: float) -> None:
    lines = [
        "=" * 70,
        f"KDP LISTING — {meta.title}",
        "=" * 70,
        "",
        "Copy each field below into the matching field in KDP's listing form at",
        "https://kdp.amazon.com → Create a new title → Paperback.",
        "",
        "-" * 70,
        "TITLE",
        "-" * 70,
        meta.title,
        "",
        "-" * 70,
        "SUBTITLE",
        "-" * 70,
        meta.subtitle,
        "",
        "-" * 70,
        "AUTHOR",
        "-" * 70,
        author_name,
        "",
        "-" * 70,
        "DESCRIPTION  (paste into 'Description' field)",
        "-" * 70,
        meta.description,
        "",
        "-" * 70,
        "KEYWORDS  (KDP allows exactly 7 — paste one per box)",
        "-" * 70,
    ]
    for i, kw in enumerate(meta.keywords, 1):
        lines.append(f"{i}. {kw}")
    lines += [
        "",
        "-" * 70,
        "CATEGORIES  (pick the 2 closest matches in KDP's category picker)",
        "-" * 70,
    ]
    for cat in meta.categories:
        lines.append(f"- {cat}")
    lines += [
        "",
        "-" * 70,
        "PRINT SETTINGS  (set these in the 'Paperback Details' step)",
        "-" * 70,
        f"Language:          English",
        f"Interior:          Black & white",
        f"Paper:             {paper.capitalize()}",
        f"Trim size:         {trim} inches",
        f"Bleed:             No bleed (interior)",
        f"Page count:        {page_count}",
        f"Cover finish:      Matte (recommended for journals)",
        f"List price (USD):  ${list_price:.2f}",
        "",
        "-" * 70,
        "ROYALTY ESTIMATE (US marketplace, B&W paperback)",
        "-" * 70,
        f"Estimated royalty per sale: ${royalty:.2f}",
        f"To earn $100/month from this book: ~{max(1, int(100/royalty))} sales/month.",
        f"To earn $1000/month from this book: ~{max(1, int(1000/royalty))} sales/month.",
        "",
        "-" * 70,
        "BSR NOTES",
        "-" * 70,
        meta.bsr_estimate,
        "",
        "-" * 70,
        "NICHE NOTES (internal, not for KDP)",
        "-" * 70,
        f"Format:      {book_type}",
        f"Niche:       {niche_obj['niche']}",
        f"Audience:    {niche_obj['audience']}",
        f"Angle:       {niche_obj['angle']}",
        "",
        "-" * 70,
        "FILES TO UPLOAD",
        "-" * 70,
        "Manuscript:  interior.pdf",
        "Book cover:  cover.pdf",
        "",
        "Tip: preview every page in KDP's online previewer before submitting.",
        "If the previewer flags a margin warning, the file is still usually fine.",
    ]
    path.write_text("\n".join(lines))


def _generate_one_book(
    book_type: str,
    niche_obj: dict,
    out_dir: Path,
    config: dict,
) -> bool:
    page_count = int(config["page_count"])
    trim = config["trim"]
    paper = config["paper"]
    author = config["author_name"]
    list_price = float(config["list_price"])

    print(f"  [meta] Generating listing metadata...")
    meta = generate_metadata(
        book_type=book_type,
        niche=niche_obj["niche"],
        audience=niche_obj["audience"],
        angle=niche_obj["angle"],
        page_count=page_count,
        trim=trim,
    )
    print(f"         Title: {meta.title}")

    book_dir = out_dir / f"{book_type}__{_slug(meta.title)}"
    book_dir.mkdir(parents=True, exist_ok=True)

    interior_path = book_dir / "interior.pdf"
    cover_path = book_dir / "cover.pdf"
    metadata_path = book_dir / "metadata.txt"

    print(f"  [interior] Building interior PDF ({page_count} pages)...")
    if book_type == "lined":
        build_lined_interior(
            out_path=interior_path,
            trim=trim,
            page_count=page_count,
            title=meta.title,
            subtitle=meta.subtitle,
            author=author,
            style="lined",
        )
    elif book_type == "prompt_journal":
        # Prompts: enough for the writing pages (page_count - 4 front matter, leave some lined-only).
        n_prompts = max(50, page_count - 8)
        print(f"  [prompts] Generating {n_prompts} unique prompts...")
        prompts = generate_prompts(niche_obj["niche"], niche_obj["audience"], n_prompts)
        build_prompt_journal_interior(
            out_path=interior_path,
            trim=trim,
            page_count=page_count,
            title=meta.title,
            subtitle=meta.subtitle,
            author=author,
            prompts=prompts,
        )
    elif book_type == "tracker":
        build_tracker_interior(
            out_path=interior_path,
            trim=trim,
            page_count=page_count,
            title=meta.title,
            subtitle=meta.subtitle,
            author=author,
        )
    elif book_type == "wordsearch":
        # Aim for ~1 puzzle every 2 content pages, leave room for solutions.
        n_puzzles = max(20, (page_count - 6) // 2)
        print(f"  [puzzles] Generating {n_puzzles} themed word lists...")
        themes = generate_wordsearch_themes(niche_obj["niche"], niche_obj["audience"], n_puzzles)
        puzzles = []
        for t in themes:
            grid_info = ws_gen.generate(t["words"], size=15, seed=hash(t["theme"]) & 0xFFFFFFFF)
            puzzles.append({
                "theme": t["theme"],
                "words": list(grid_info["positions"].keys()),  # only placed words
                "grid": grid_info["grid"],
                "positions": grid_info["positions"],
            })
        build_wordsearch_interior(
            out_path=interior_path,
            trim=trim,
            page_count=page_count,
            title=meta.title,
            subtitle=meta.subtitle,
            author=author,
            puzzles=puzzles,
        )
    else:
        print(f"  [!] Unknown book_type: {book_type}")
        return False

    print(f"  [cover] Building wrap cover PDF...")
    # Back-cover blurb: first 2-3 lines of the description.
    blurb = meta.description.split("\n\n")[0].strip()
    if len(blurb) > 600:
        blurb = blurb[:600].rsplit(" ", 1)[0] + "..."
    build_cover(
        title=meta.title,
        subtitle=meta.subtitle,
        author=author,
        back_blurb=blurb,
        trim=trim,
        page_count=page_count,
        paper=paper,
        out_path=cover_path,
        style_seed=niche_obj["niche"],
    )

    royalty = estimate_royalty(list_price, page_count)
    _write_metadata_file(
        metadata_path, meta, book_type, niche_obj,
        page_count, trim, paper, author, list_price, royalty,
    )

    print(f"  [done] {book_dir.name}/")
    print(f"         interior.pdf | cover.pdf | metadata.txt")
    return True


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    _check_env()

    config = yaml.safe_load((KDP_ROOT / "config.yaml").read_text())

    theme = config["theme"]
    book_types = config["book_types"]
    books_per_type = int(config["books_per_type"])
    avoid_repeats = bool(config.get("avoid_repeats", True))

    today = dt.date.today().isoformat()
    out_dir = KDP_ROOT / "output" / today
    out_dir.mkdir(parents=True, exist_ok=True)

    history_path = KDP_ROOT / "cache" / "niches_used.json"
    used = _load_history(history_path) if avoid_repeats else []

    print(f"\n=== House of Hudson — KDP Auto-Publishing ===")
    print(f"Theme:           {theme}")
    print(f"Book types:      {', '.join(book_types)}")
    print(f"Per type:        {books_per_type}")
    print(f"Output:          {out_dir}")
    print()

    successes = 0
    failures = 0

    for book_type in book_types:
        print(f"\n--- Brainstorming {books_per_type} niche(s) for: {book_type} ---")
        try:
            ideas = brainstorm(theme, book_type, books_per_type, avoid=used)
        except Exception as e:
            print(f"  [!] Niche brainstorm failed for {book_type}: {e}")
            failures += 1
            continue

        for niche_obj in ideas[:books_per_type]:
            print(f"\n>> {book_type} — {niche_obj['niche']}")
            print(f"   Audience: {niche_obj['audience']}")
            try:
                ok = _generate_one_book(book_type, niche_obj, out_dir, config)
                if ok:
                    successes += 1
                    used.append(niche_obj["niche"])
                else:
                    failures += 1
            except Exception as e:
                print(f"  [!] Book generation failed: {e}")
                traceback.print_exc()
                failures += 1

    if avoid_repeats:
        _save_history(history_path, used)

    print()
    print(f"=== Finished: {successes} books generated, {failures} failed ===")
    print(f"    Output folder: {out_dir}")
    print()
    print("Next steps:")
    print("  1. Open each book folder above")
    print("  2. Open interior.pdf and cover.pdf to preview")
    print("  3. Go to https://kdp.amazon.com → 'Create' → 'Paperback'")
    print("  4. Copy fields from metadata.txt into each step of the form")
    print("  5. Upload interior.pdf as manuscript, cover.pdf as book cover")
    print("  6. Submit for review (Amazon usually approves within 72h)")
    print()
    print("Tip: don't upload all books on day one. Spread to 1-3 per day across")
    print("     2-3 weeks to keep your KDP account in good standing.")
    return 0 if successes > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
