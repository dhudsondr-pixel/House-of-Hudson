"""Brainstorm specific, sellable niche+audience combinations for KDP books."""
from __future__ import annotations

import json
import os
import re
from typing import List

from anthropic import Anthropic

MODEL = "claude-opus-4-7"


def _strip_fence(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def brainstorm(theme: str, book_type: str, count: int, avoid: List[str]) -> List[dict]:
    """Return list of {"niche": str, "audience": str, "angle": str} ideas.

    'theme' is the broad area (e.g. "self-care", "fitness", "productivity").
    'book_type' is one of: lined, prompt_journal, tracker, wordsearch.
    """
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    avoid_str = "\n".join(f"- {t}" for t in avoid[-50:]) if avoid else "(none yet)"

    type_hints = {
        "lined": "A simple lined notebook/journal — sellable as a niched gift item.",
        "prompt_journal": "A prompt-driven journal with daily reflection prompts.",
        "tracker": "A habit/goal tracker with monthly grids and weekly review pages.",
        "wordsearch": "A themed word search puzzle book for a specific interest group.",
        "diabetes_log": (
            "A 90-day clinical daily log book for someone managing type 2 diabetes. "
            "One page per day: glucose readings (pre/post meal), carbs by meal, "
            "medications + insulin, activity, sleep, mood, notes. Plus baseline + "
            "goals + care-team pages. Each sub-niche should target a DISTINCT patient "
            "framing — e.g. newly diagnosed adults, women over 50, pre-bariatric, "
            "type 2 with insulin, gestational diabetes companions, prediabetes turn-around. "
            "Each niche needs a clear emotional/situational hook."
        ),
        "adhd_planner": (
            "A 90-day adult ADHD daily planner. One page per day: top-3 priorities "
            "(not long todo lists), stimulant + other meds tracking, 8 loose time "
            "blocks, morning/midday/evening focus & energy ratings, distraction-park "
            "lines (for capturing intrusive thoughts during deep work), end-of-day "
            "win + lesson + carry-forward. Plus baseline ADHD profile, 90-day goals, "
            "care team, medication trial log. Each sub-niche should target a "
            "DISTINCT adult-ADHD framing — e.g. newly diagnosed adults, women with "
            "late-diagnosed ADHD, university students, parents of ADHD kids who "
            "are themselves ADHD, ADHD + autism, ADHD with anxiety, professionals "
            "navigating workplace, ADHD medication titration journal. Each needs a "
            "clear identity/situational hook."
        ),
    }
    type_hint = type_hints.get(book_type, "")

    prompt = f"""Brainstorm {count} specific, commercially viable KDP book niches.

Broad theme: {theme}
Book format: {book_type} — {type_hint}

For each idea, output a JSON object with:
- "niche": the specific sub-niche (e.g. "Marathon Training", not just "Fitness")
- "audience": the buyer persona in 4-8 words (e.g. "first-time marathon runners over 40")
- "angle": what makes this listing distinct in 10-15 words

What makes a good KDP niche:
- Specific enough that buyers self-identify and Amazon search has manageable competition
- A clear gift-giving occasion or self-bought purpose
- An emotional or identity hook (people buy books that signal who they are)
- NOT oversaturated generic terms like "Gratitude Journal" with no qualifier

Niches to AVOID (already done):
{avoid_str}

Output strict JSON only: {{"ideas": [{{"niche": "...", "audience": "...", "angle": "..."}}, ...]}}"""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    data = json.loads(_strip_fence(resp.content[0].text))
    return data["ideas"]
