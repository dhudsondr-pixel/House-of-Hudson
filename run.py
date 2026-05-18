#!/usr/bin/env python3
"""House of Hudson — automated short-form video generator.

Run with:  python run.py

Reads settings from config.yaml and API keys from .env.
Outputs finished MP4s + a captions.txt into ./output/<date>/.
"""
from __future__ import annotations

import datetime as dt
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src import history
from src.footage import fetch_clips
from src.script import generate_script, generate_topic_ideas
from src.video import assemble
from src.voice import synthesize


def _slug(text: str) -> str:
    keep = "abcdefghijklmnopqrstuvwxyz0123456789-"
    s = text.lower().replace(" ", "-")
    return "".join(c for c in s if c in keep)[:60]


def _check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        print("\n[!] ffmpeg is not installed. moviepy needs it.")
        print("    macOS:    brew install ffmpeg")
        print("    Ubuntu:   sudo apt-get install ffmpeg")
        print("    Windows:  https://ffmpeg.org/download.html")
        sys.exit(1)


def _check_env() -> None:
    import os
    missing = [k for k in ("ANTHROPIC_API_KEY", "PEXELS_API_KEY") if not os.environ.get(k)]
    if missing:
        print(f"\n[!] Missing required env vars: {', '.join(missing)}")
        print("    Copy .env.example to .env and fill in your keys.")
        print("    Anthropic: https://console.anthropic.com/")
        print("    Pexels (free): https://www.pexels.com/api/")
        sys.exit(1)


def main() -> int:
    load_dotenv(ROOT / ".env")
    _check_env()
    _check_ffmpeg()

    config = yaml.safe_load((ROOT / "config.yaml").read_text())

    niche = config["niche"]
    n_videos = int(config.get("videos_per_run", 3))
    target_seconds = int(config.get("target_seconds", 35))
    voice = config.get("voice", "en-us-female")
    style = config.get("style", "facts")
    resolution = config.get("resolution", "1080x1920")
    aspect_ratio = config.get("aspect_ratio", "9:16")
    channel_name = config.get("channel_name", "") or ""
    avoid_repeats = bool(config.get("avoid_repeats", True))

    prefer_vertical = aspect_ratio.startswith("9:")
    today = dt.date.today().isoformat()
    out_dir = ROOT / "output" / today
    out_dir.mkdir(parents=True, exist_ok=True)

    history_path = ROOT / "cache" / "topics_used.json"
    used = history.load(history_path) if avoid_repeats else []

    print(f"\n=== House of Hudson ===")
    print(f"Niche:    {niche}")
    print(f"Videos:   {n_videos}")
    print(f"Length:   ~{target_seconds}s each")
    print(f"Output:   {out_dir}")
    print()

    print("[1/4] Brainstorming topic ideas...")
    try:
        topics = generate_topic_ideas(niche, n_videos, avoid=used[-100:])
    except Exception as e:
        print(f"[!] Topic brainstorm failed: {e}")
        return 1
    print(f"      Got {len(topics)} topics.")
    for t in topics:
        print(f"        - {t}")

    captions_lines: list[str] = []
    successes = 0

    for i, topic in enumerate(topics, 1):
        print(f"\n[2/4] ({i}/{len(topics)}) Writing script for: {topic}")
        try:
            script = generate_script(niche, target_seconds, style, topic_hint=topic)
        except Exception as e:
            print(f"    [!] Script generation failed: {e}")
            continue
        print(f"      Title: {script.title}")

        # Use a temp dir per video for stock clip downloads (cleaned up after).
        with tempfile.TemporaryDirectory(prefix="hoh_clips_") as tmp_str:
            tmp = Path(tmp_str)

            print(f"[3/4] ({i}/{len(topics)}) Generating voiceover...")
            audio_path = tmp / "voice.mp3"
            try:
                synthesize(script.full_narration(), voice, audio_path)
            except Exception as e:
                print(f"    [!] Voice synthesis failed: {e}")
                continue

            print(f"      Fetching stock footage...")
            try:
                clips = fetch_clips(
                    keywords=script.visual_keywords,
                    out_dir=tmp,
                    count=max(4, target_seconds // 5),
                    prefer_vertical=prefer_vertical,
                )
            except Exception as e:
                print(f"    [!] Footage fetch failed: {e}")
                continue

            print(f"[4/4] ({i}/{len(topics)}) Assembling video...")
            video_filename = f"{i:02d}_{_slug(script.title)}.mp4"
            video_out = out_dir / video_filename
            try:
                assemble(
                    clip_paths=clips,
                    audio_path=audio_path,
                    captions=script.on_screen_captions,
                    out_path=video_out,
                    resolution=resolution,
                    channel_name=channel_name,
                )
            except Exception as e:
                print(f"    [!] Video assembly failed: {e}")
                traceback.print_exc()
                continue

        successes += 1
        used.append(topic)
        captions_lines.append(f"=== {video_filename} ===")
        captions_lines.append(f"Title: {script.title}")
        captions_lines.append("")
        captions_lines.append("Caption / Description (paste into YouTube/TikTok):")
        captions_lines.append(f"{script.hook} {script.narration}")
        captions_lines.append("")
        captions_lines.append("Suggested tags / hashtags:")
        tags = " ".join(f"#{kw.replace(' ', '')}" for kw in script.visual_keywords[:6])
        captions_lines.append(tags)
        captions_lines.append("")
        captions_lines.append("---")
        captions_lines.append("")
        print(f"      DONE: {video_out.name}")

    (out_dir / "captions.txt").write_text("\n".join(captions_lines))

    if avoid_repeats:
        history.save(history_path, used)

    print()
    print(f"=== Finished: {successes}/{len(topics)} videos generated ===")
    print(f"    Output folder: {out_dir}")
    print(f"    Captions/descriptions: {out_dir / 'captions.txt'}")
    print()
    print("Next steps:")
    print("  1. Open the output folder above")
    print("  2. Preview each MP4")
    print("  3. Upload to YouTube Shorts / TikTok with the captions from captions.txt")
    print("  4. Post consistently — daily if possible — for at least 30 days")
    return 0 if successes > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
