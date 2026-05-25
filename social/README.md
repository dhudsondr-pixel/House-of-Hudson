# House of Hudson — Social Media Content Factory

A tool that drafts your daily cross-platform social content — Pinterest pins, Instagram quotes and carousels, Twitter/X threads, and TikTok scripts — and outputs them as ready-to-upload files. You review, click-to-schedule via the platforms' free native schedulers, and the channels grow on autopilot.

This tool is the **marketing arm** of the House of Hudson 3D printing stack. It promotes your STL listings (Cults3D, MakerWorld, Printables, Etsy) and drives custom-order inquiries.

---

## The honest expectations

**"Millions of followers" is the lottery-ticket outcome, not the planning baseline.** A specific brand account hits a 1M follower milestone roughly 1 in 500 attempts. What's realistic with daily posting in a 3D-printing niche for 12 months:

| Platform | 12-month realistic follower band | What it drives |
|---|---|---|
| Pinterest | 100-10k followers | **1k-100k+ monthly impressions → STL downloads + custom orders** (this is the moneymaker for 3D printing) |
| Instagram | 1k-50k | Maker community recognition, organic DM custom-order requests |
| TikTok | 1k-100k+ (high variance) | One viral print timelapse can spike STL downloads by 10x for weeks |
| Twitter/X | 500-5k | Slow growth but well-connected to the maker community |

**Across all four**, you can absolutely hit 100k+ total followers and millions of monthly impressions in year 2, if you're consistent and the niche is right. But the real win is **MakerWorld / Cults3D download counts and DM-based custom-order leads**.

### Will not be automated

- **Engagement automation** (auto-liking, auto-commenting, auto-following). Every major platform bans accounts that do this — usually within 7-14 days. The tool will not do it.
- **Direct posting via APIs**. Pinterest, Instagram, TikTok, and Twitter/X all require app approval (1-4 weeks each), and some have monthly fees. The friction isn't worth it for a one-person operation. Their native schedulers are free and good — see below.

---

## What it produces

Each run creates one folder per platform:

```
social/output/2026-05-25/
  pinterest/
    01_<hook-slug>.png        # 1000x1500, ready to upload
    01_<hook-slug>.txt        # title + description + hashtags + link
    02_..., 03_..., ...
  instagram/
    quote_01_<slug>.png       # 1080x1080
    quote_01_<slug>.txt
    carousel_01_<slug>/
      slide_1.png ... slide_N.png   # 1080x1350 each
      caption.txt
  twitter/
    thread_01.txt              # tweets separated, copy-paste ready
  tiktok/
    script_01.txt              # hook + narration + captions + B-roll keywords
```

Pin styles rotate across 4 templates (bold headline, quote, tip, listicle). Palettes default to maker-themed ones (industrial, blueprint, graphite, lab) so the feed feels consistent with a 3D printing brand.

---

## Daily use

### 1. Edit `social/config.yaml` once

- `brand_name`: your business name (default: "House of Hudson")
- `niche` & `audience`: describe what you make and who buys it
- `link_in_bio`: where you want clicks to land — your Cults3D profile, MakerWorld profile, Etsy shop, or a Linktree linking to all of them
- `featured_design_dir`: optional — point at a folder in `stl/output/` to focus today's posts on a specific design you just listed

### 2. Run

```bash
bash social/run_social.sh        # Mac/Linux
social/run_social.bat            # Windows
```

### 3. Open the output folder, preview, upload

The integration with the STL tool: when you list a new design via `stl/run.py`, point `featured_design_dir:` at that output folder. The strategist will read the design's analysis + Cults3D listing copy and write social posts that promote *that specific design*.

---

## Upload workflow (30-40 min/day, can be batched weekly)

### Pinterest (most important for 3D printing — start here)

Pinterest is where people search "3D printed gift for engineer" or "useful 3D prints" with buyer intent. It's the highest-ROI platform for selling printed/listed items.

1. https://business.pinterest.com → switch to a free business account
2. Verify your shop URL under "Settings → Claim" (Etsy / Cults3D / your own site)
3. For each pin in the output folder:
   - "Create" → "Create Pin"
   - Upload the PNG
   - Paste title, description, hashtags, and destination link from the .txt file
   - Click "Publish at later date" → schedule
4. Free scheduler holds 100 pins. Schedule a week in one sitting.
5. Cadence: 5-10 pins/day spread 8am-10pm in your audience's timezone.

### Instagram

1. Link IG to https://business.facebook.com (Meta Business Suite)
2. Click "Planner" → "Create Post"
3. For carousels: drag all `slide_*.png` files in order, paste the caption
4. For quotes: upload the single PNG with its caption
5. Cadence: 1-2 posts/day

### Twitter/X

1. Open each `thread_XX.txt`
2. Post tweet 1, reply with tweet 2, etc.
3. Or use https://typefully.com (free for 4 scheduled posts/month)

### TikTok / Reels / Shorts

The script file has hook + narration + on-screen captions + B-roll keywords. Two ways to make the video:

**Option A — fully automated:** use the video generator at the repo root.
- Copy the niche from `social/config.yaml` into the top-level `config.yaml`
- Run `bash run.sh`
- Upload the MP4s

**Option B — your own footage (better for 3D printing):** record your printer mid-print, post-process timelapses with your phone, narrate the script. ~15 min per video. **Real print timelapses outperform stock footage 10:1 for 3D printing content** — if you can do this for at least your hero designs, do.

---

## Strategy: getting traffic to your STLs

| Phase | What you do | Where the traffic comes from |
|---|---|---|
| **Weeks 1-4** | Pin 5-10/day from your top 5 STL listings, post 1 IG/day, 1 video/day. Don't read stats. | Nowhere yet — you're seeding |
| **Weeks 5-12** | Look at Pinterest analytics. Find your top 5 pins. Make 10 variants of each (same design, different angles/hooks). Drop everything else. | Pinterest starts pushing the winners. Expect 1k-10k monthly impressions. |
| **Months 3-6** | Double down on winning design niches. Each new STL launch becomes a Pinterest sprint (15-20 pins for that one STL in a week). | Pinterest 50k-500k monthly impressions. STL downloads + custom orders start. |
| **Months 6-12** | Repurpose top Pinterest pin hooks into TikTok. A viral 3D printing TikTok = MakerWorld download spike. | Multi-platform compound. 100k-1M monthly impressions. |
| **Months 12+** | Add $5/day Pinterest Ads on top performers, $5/day Etsy Ads on your printed-version listings. | Paid amplification on winners only. |

The real lever is **Pinterest pin volume tied to specific listings**. This tool produces 8 pins per run × daily = 240 pins/month. In a year you'll have a library of 2,000+ pins compounding for your top designs.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ANTHROPIC_API_KEY not set` | Paste your key into `.env` at the repo root. |
| Pins all look similar | Add more palettes to `allowed_palettes` in `config.yaml`, or remove the list to use all 8. |
| Hook quality uneven | Run again — Claude generates fresh angles each run. Or tighten `niche:` (more specific = better hooks). |
| Pinterest rejects pins | Almost always because the destination URL isn't claimed. Claim your shop URL in Pinterest settings. |
| Content sounds generic | Set `featured_design_dir:` to a specific STL output folder. Specific-design posts massively outperform brand-only posts. |

If anything errors, paste the message and I'll fix it.
