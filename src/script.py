"""Generate a short-form video script using Claude."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import List

from anthropic import Anthropic

MODEL = "claude-opus-4-7"


@dataclass
class VideoScript:
    title: str
    hook: str
    narration: str
    on_screen_captions: List[str]
    visual_keywords: List[str]
    cta: str

    def full_narration(self) -> str:
        return f"{self.hook} {self.narration} {self.cta}".strip()


SYSTEM_PROMPT = """You are a viral short-form video scriptwriter.
You write tight, punchy scripts for YouTube Shorts and TikTok that hook viewers in the first 2 seconds and retain them to the end.

Rules:
- The HOOK must be a single sentence that creates immediate curiosity or shock. No filler words like "Did you know" or "Today we're going to talk about".
- The narration body should be conversational, vivid, and avoid jargon. Read out loud naturally.
- Total spoken word count must hit the target length (~2.5 words per second of audio).
- Visual keywords are short search queries (1-3 words) for stock footage that matches each segment.
- On-screen captions are 3-5 ultra-short text overlays (max 5 words each) that appear during key moments.
- The CTA should be subtle: "Follow for more" or "Part 2 tomorrow" — NEVER aggressive.

Output strict JSON only, no prose, no markdown, no commentary. Schema:
{
  "title": string (the video title, under 70 chars, designed for clicks),
  "hook": string (one sentence, opens the video),
  "narration": string (the main body of the script),
  "on_screen_captions": [string, ...] (3-5 short overlays),
  "visual_keywords": [string, ...] (5-8 stock footage search terms),
  "cta": string (closing line)
}"""


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_script(niche: str, target_seconds: int, style: str, topic_hint: str | None = None) -> VideoScript:
    """Generate one video script. Raises on API or parse error."""
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    target_words = int(target_seconds * 2.5)

    user_prompt = f"""Niche: {niche}
Style: {style}
Target length: {target_seconds} seconds (about {target_words} words spoken)
{f"Topic hint: {topic_hint}" if topic_hint else "Pick a fresh, specific topic in this niche that hasn't been done to death."}

Write the script now. Output JSON only."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = response.content[0].text
    data = json.loads(_strip_json_fence(raw))

    return VideoScript(
        title=data["title"],
        hook=data["hook"],
        narration=data["narration"],
        on_screen_captions=data["on_screen_captions"],
        visual_keywords=data["visual_keywords"],
        cta=data["cta"],
    )


def generate_topic_ideas(niche: str, count: int, avoid: List[str]) -> List[str]:
    """Brainstorm distinct topic ideas so videos in one run don't overlap."""
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    avoid_str = "\n".join(f"- {t}" for t in avoid) if avoid else "(none yet)"

    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""Brainstorm {count} fresh, specific video topic ideas for a short-form channel about: {niche}

Topics must be:
- Distinct from each other (no overlap)
- Specific enough to make a 30-second video about (not generic)
- Surprising, counterintuitive, or visually engaging

Topics to AVOID (already covered):
{avoid_str}

Output JSON only: {{"topics": ["topic 1", "topic 2", ...]}}"""
        }],
    )

    raw = _strip_json_fence(response.content[0].text)
    return json.loads(raw)["topics"]
