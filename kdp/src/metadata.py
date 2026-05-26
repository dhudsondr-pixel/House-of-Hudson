"""Generate KDP listing metadata: title, subtitle, description, keywords, categories."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import List

from anthropic import Anthropic

MODEL = "claude-opus-4-7"


@dataclass
class BookMetadata:
    title: str
    subtitle: str
    description: str        # 4000-char HTML-safe description for KDP listing
    keywords: List[str]     # exactly 7
    categories: List[str]   # 2 suggested KDP browse categories
    bsr_estimate: str       # text estimate of competitiveness


def _strip_fence(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


SYSTEM_PROMPT = """You are a KDP listing optimization expert.
You write titles, subtitles, descriptions, and keywords that rank in Amazon search and convert browsers to buyers.

Hard rules:
- Title: max 60 characters. Lead with the primary search keyword. No emoji, no quotes.
- Subtitle: 8-20 words. Describes the buyer/use-case. Often the secondary keyword.
- Description: 200-400 words. Hook → buyer's pain → what's inside (bulleted) → who it's for → closer. Plain text only; use line breaks. Do NOT include the words "AI" or "ChatGPT" anywhere. No fake quotes/testimonials.
- Keywords: exactly 7. Each must be a phrase a real buyer would TYPE into Amazon search. No repeats of the title words. Mix broad and specific. Max 50 chars each.
- Categories: 2 from KDP's published category tree. Pick categories where this niche book can plausibly rank top-100.
- bsr_estimate: one line, e.g. "Mid-competition: top-100 in category achievable with 5-15 reviews."

Output strict JSON only. Schema:
{
  "title": string,
  "subtitle": string,
  "description": string,
  "keywords": [string, string, string, string, string, string, string],
  "categories": [string, string],
  "bsr_estimate": string
}"""


def generate_metadata(
    book_type: str,
    niche: str,
    audience: str,
    angle: str,
    page_count: int,
    trim: str,
    template_contents: str | None = None,
) -> BookMetadata:
    """Generate listing metadata.

    `template_contents`: optional verbatim description of what's actually inside
    the printed interior. When provided, the generated description is constrained
    to ONLY promise features that the template actually delivers (no overselling).
    """
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    template_block = ""
    if template_contents:
        template_block = f"""

CRITICAL — the interior of this book contains EXACTLY the following and nothing
more. The description must accurately describe these contents. Do NOT invent
features that are not listed here. Do NOT promise any clinical recommendations,
food databases, treatment plans, or anything not in this list.

{template_contents}
"""

    user_prompt = f"""Generate KDP listing metadata for this book.

Book format: {book_type}
Niche: {niche}
Target audience: {audience}
Differentiation angle: {angle}
Page count: {page_count}
Trim size: {trim} inches
{template_block}
Write the listing now. JSON only."""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    data = json.loads(_strip_fence(resp.content[0].text))

    kws = data["keywords"]
    # Defensive: ensure 7 keywords, truncate or pad.
    while len(kws) < 7:
        kws.append(niche.lower())
    kws = kws[:7]

    return BookMetadata(
        title=data["title"],
        subtitle=data["subtitle"],
        description=data["description"],
        keywords=kws,
        categories=data["categories"],
        bsr_estimate=data.get("bsr_estimate", ""),
    )


def generate_prompts(niche: str, audience: str, count: int) -> List[str]:
    """Generate `count` distinct reflection prompts for a prompt journal."""
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    batch_size = 30
    all_prompts: List[str] = []
    while len(all_prompts) < count:
        remaining = count - len(all_prompts)
        n = min(batch_size, remaining)
        already = "\n".join(f"- {p}" for p in all_prompts[-30:]) if all_prompts else "(none yet)"

        resp = client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": f"""Generate {n} distinct, thoughtful journal prompts for this audience.

Niche: {niche}
Audience: {audience}

Each prompt should:
- Be one or two sentences (under 25 words)
- Invite specific, concrete reflection (not generic)
- Avoid New Age platitudes
- Connect to the audience's real life
- Not repeat earlier prompts

Already used (don't repeat):
{already}

Output strict JSON only: {{"prompts": ["...", "...", ...]}}"""
            }],
        )
        data = json.loads(_strip_fence(resp.content[0].text))
        new = [p.strip() for p in data["prompts"] if p.strip()]
        if not new:
            break
        all_prompts.extend(new)

    return all_prompts[:count]


def generate_wordsearch_themes(niche: str, audience: str, puzzle_count: int) -> List[dict]:
    """For a word search book, generate a list of {"theme": str, "words": [str,...]} per puzzle."""
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    resp = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Generate {puzzle_count} word search puzzle themes for this audience.

Niche: {niche}
Audience: {audience}

Each puzzle needs:
- A theme name (3-6 words, evocative)
- Exactly 15 words, each 4-12 letters long, ALL CAPS, letters A-Z only (no spaces, no punctuation, no numbers)
- Words must be thematically tied to the puzzle theme and feel relevant to the audience
- No duplicate words within a puzzle
- No duplicate themes across the book

Output strict JSON only:
{{"puzzles": [{{"theme": "...", "words": ["WORD1", "WORD2", ..., "WORD15"]}}, ...]}}"""
        }],
    )
    data = json.loads(_strip_fence(resp.content[0].text))
    # Sanitize words.
    out = []
    for p in data["puzzles"]:
        cleaned = [re.sub(r"[^A-Z]", "", w.upper()) for w in p["words"]]
        cleaned = [w for w in cleaned if 4 <= len(w) <= 12]
        if len(cleaned) >= 10:
            out.append({"theme": p["theme"], "words": cleaned[:15]})
    return out
