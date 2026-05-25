"""Text-only post writers: Twitter/X threads + TikTok scripts."""
from __future__ import annotations

from pathlib import Path
from typing import List


def write_thread(path: Path, tweets: List[str], topic: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["=== Twitter / X Thread ===", ""]
    if topic:
        lines += [f"Topic: {topic}", ""]
    lines += ["Post these one at a time as a thread (reply each to the previous):", ""]
    for i, tweet in enumerate(tweets, 1):
        tweet = tweet.strip()
        # Hard cap at 280 to be safe.
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        lines.append(f"--- Tweet {i}/{len(tweets)} ({len(tweet)} chars) ---")
        lines.append(tweet)
        lines.append("")
    path.write_text("\n".join(lines))
    return path


def write_tiktok_script(
    path: Path,
    hook: str,
    narration: str,
    captions: List[str],
    visual_keywords: List[str],
    cta: str,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "=== TikTok / Reels / Shorts Script ===",
        "",
        "HOOK (first 2 seconds — say this with energy):",
        hook.strip(),
        "",
        "NARRATION (read the hook + this body + the CTA out loud):",
        narration.strip(),
        "",
        "CTA (close):",
        cta.strip(),
        "",
        "ON-SCREEN CAPTIONS (overlay these during the video):",
    ]
    for c in captions:
        lines.append(f"  - {c}")
    lines += [
        "",
        "B-ROLL / STOCK FOOTAGE KEYWORDS:",
    ]
    for kw in visual_keywords:
        lines.append(f"  - {kw}")
    lines += [
        "",
        "---",
        "TO TURN THIS INTO A FINISHED VIDEO:",
        "1. The video tool in this repo (../run.py) can auto-produce vertical MP4s from",
        "   a similar config. Update its config.yaml niche and run `bash run.sh`.",
        "2. Or record this yourself in a single take using your phone's front camera.",
        "3. Upload to TikTok / Instagram Reels / YouTube Shorts with the caption below.",
        "",
        "CAPTION FOR UPLOAD:",
        hook.strip() + " " + cta.strip(),
    ]
    path.write_text("\n".join(lines))
    return path
