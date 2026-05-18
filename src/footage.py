"""Fetch stock video clips from Pexels (free API)."""
from __future__ import annotations

import os
import random
from pathlib import Path
from typing import List, Optional

import requests

PEXELS_VIDEO_SEARCH = "https://api.pexels.com/videos/search"


def _pick_file(video_files: list, prefer_vertical: bool) -> Optional[dict]:
    """Pick the best mp4 from a Pexels video's files list."""
    mp4s = [f for f in video_files if f.get("file_type") == "video/mp4" and f.get("link")]
    if not mp4s:
        return None
    if prefer_vertical:
        vertical = [f for f in mp4s if f.get("height", 0) >= f.get("width", 0)]
        if vertical:
            mp4s = vertical
    # Prefer ~720p quality for balance of size/speed.
    mp4s.sort(key=lambda f: abs((f.get("height") or 720) - 720))
    return mp4s[0]


def fetch_clips(
    keywords: List[str],
    out_dir: Path,
    count: int,
    prefer_vertical: bool = True,
) -> List[Path]:
    """Download `count` short stock video clips matching the keywords.
    Falls back to broader queries if no results."""
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "PEXELS_API_KEY not set. Get a free key at https://www.pexels.com/api/"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    headers = {"Authorization": api_key}

    clip_paths: List[Path] = []
    pool: List[dict] = []
    seen_ids: set = set()

    # Build a pool of candidate clips from each keyword.
    for kw in keywords:
        try:
            r = requests.get(
                PEXELS_VIDEO_SEARCH,
                params={"query": kw, "per_page": 8, "orientation": "portrait" if prefer_vertical else "landscape"},
                headers=headers,
                timeout=20,
            )
            r.raise_for_status()
            for v in r.json().get("videos", []):
                if v["id"] in seen_ids:
                    continue
                seen_ids.add(v["id"])
                pool.append(v)
        except Exception as e:
            print(f"  [warn] Pexels search failed for '{kw}': {e}")

    # Fallback: generic "nature" / "city" / "abstract" if the niche queries yielded nothing.
    if not pool:
        print("  [warn] No niche clips found, falling back to generic queries.")
        for kw in ["nature", "city", "abstract motion"]:
            try:
                r = requests.get(
                    PEXELS_VIDEO_SEARCH,
                    params={"query": kw, "per_page": 8, "orientation": "portrait" if prefer_vertical else "landscape"},
                    headers=headers,
                    timeout=20,
                )
                r.raise_for_status()
                for v in r.json().get("videos", []):
                    pool.append(v)
            except Exception:
                pass

    random.shuffle(pool)

    for v in pool:
        if len(clip_paths) >= count:
            break
        f = _pick_file(v.get("video_files", []), prefer_vertical)
        if not f:
            continue
        url = f["link"]
        path = out_dir / f"clip_{v['id']}.mp4"
        try:
            with requests.get(url, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                with open(path, "wb") as fh:
                    for chunk in resp.iter_content(chunk_size=1 << 16):
                        fh.write(chunk)
            clip_paths.append(path)
        except Exception as e:
            print(f"  [warn] Download failed for clip {v['id']}: {e}")

    if not clip_paths:
        raise RuntimeError("Could not download any stock clips. Check your Pexels API key and internet.")

    return clip_paths
