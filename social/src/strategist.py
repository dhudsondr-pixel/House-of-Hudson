"""Generate a daily cross-platform content brief tailored to a brand + niche."""
from __future__ import annotations

import json
import os
import re
from typing import List

from anthropic import Anthropic

MODEL = "claude-opus-4-7"


def _strip(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


SYSTEM = """You are a social media content strategist specializing in growing
3D printing brands across Pinterest, Instagram, TikTok, and Twitter/X.

Your job: generate a daily content plan for a 3D printing business that designs
and sells STL files AND offers print-on-demand custom orders. The content should
showcase their work (designs, prints, timelapses), build a maker-community
following, and drive viewers to their STL listings (Cults3D, MakerWorld,
Printables, Etsy) or their custom-order intake.

Output strict JSON only. Schema:
{
  "pinterest_pins": [
    {"hook": "8-12 word headline that creates curiosity/desire",
     "subhead": "5-9 word supporting line",
     "style": "bold|quote|tip|listicle",
     "description": "200-400 char Pinterest description with natural keyword usage",
     "hashtags": ["#tag", "#tag", ...]  // 5-10 lowercase, niche-relevant
    }, ...
  ],
  "instagram_quotes": [
    {"quote": "the quote text, 8-20 words, evocative not preachy",
     "caption": "2-4 paragraph IG caption, conversational, ends with soft CTA",
     "hashtags": ["#tag", ...]  // 10-20 tags mixing broad+niche
    }, ...
  ],
  "instagram_carousels": [
    {"hook": "slide-1 hook, 6-10 words",
     "slides": [
       {"heading": "short", "body": "30-60 char body"},
       ... 3 to 4 middle slides ...
       {"heading": "final CTA", "body": "soft CTA pointing toward the book"}
     ],
     "caption": "150-300 word caption that expands on the carousel",
     "hashtags": ["#tag", ...]
    }, ...
  ],
  "twitter_threads": [
    {"tweets": ["tweet 1 text (under 270 chars)", "tweet 2", ..., "final tweet w/ soft CTA"],
     "topic": "one-line topic summary"
    }, ...
  ],
  "tiktok_scripts": [
    {"hook": "2-3 sec opening line, must stop scroll",
     "narration": "30-45 second spoken script",
     "captions": ["3-5 short on-screen overlay texts"],
     "visual_keywords": ["3-6 stock footage search terms"],
     "cta": "subtle closing line"
    }, ...
  ]
}

Rules across all platforms:
- Never sound like an ad. Sound like a maker sharing their craft.
- Never claim the design is "AI-generated" anywhere.
- Use real 3D printing language: layer lines, supports, bed adhesion, retraction,
  PLA/PETG/TPU, infill %, brim, raft, FDM, resin, slicer, supports tree/normal,
  benchy, calibration cube — but explain where helpful for newer audiences.
- Mix content types: design reveals, timelapse stills, problem-solved-by-printing
  posts, tips & tricks, behind-the-scenes process, failed prints (relatable),
  customer print showcases.
- All CTAs should be soft: "save for your next print queue", "free on
  MakerWorld / Printables", "the STL is on Cults", "DM to print one for you".
- Pinterest pins especially: lead with a SPECIFIC visual hook ("This 30-minute
  print solved my cable mess") not vague vibes ("Beautiful 3D print").
- Vary content style across posts so the feed doesn't feel repetitive.
- Hooks and captions must feel native to each platform's voice."""


def generate_plan(
    brand_name: str,
    niche: str,
    audience: str,
    tagline: str,
    design_context: str,
    n_pinterest: int = 5,
    n_ig_quotes: int = 1,
    n_ig_carousels: int = 1,
    n_threads: int = 1,
    n_tiktok: int = 1,
) -> dict:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user = f"""Generate today's social content plan.

Brand:     {brand_name}
Niche:     {niche}
Audience:  {audience}
Tagline:   {tagline}

Featured design / focus for today:
{design_context}

Quantities for this run:
- Pinterest pins:     {n_pinterest}
- Instagram quotes:   {n_ig_quotes}
- Instagram carousels: {n_ig_carousels}
- Twitter threads:    {n_threads}
- TikTok scripts:     {n_tiktok}

Output the JSON plan now."""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=6000,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    return json.loads(_strip(resp.content[0].text))
