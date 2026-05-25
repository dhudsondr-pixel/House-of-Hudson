# House of Hudson — Social Media Content Factory

A tool that drafts your daily cross-platform social content — Pinterest pins, Instagram quotes and carousels, Twitter/X threads, and TikTok scripts — and outputs them as ready-to-upload files. You review, click-to-schedule via the platforms' free native schedulers, and your channels grow on autopilot.

This tool sits next to the KDP auto-publisher and the video generator in this same repo. It's designed to **promote the books you're publishing**.

---

## The honest expectations

**"Millions of followers" is the lottery-ticket outcome, not the planning baseline.** A specific brand account hits a 1M follower milestone roughly 1 in 500 attempts. What's realistic with daily posting in a tight niche for 12 months:

| Platform | 12-month realistic follower band | What it drives |
|---|---|---|
| Pinterest | 100-10k followers | **1k-100k+ monthly impressions → book traffic** (this is the moneymaker) |
| Instagram | 1k-50k | Brand recognition, soft sales |
| TikTok | 1k-100k+ (high variance) | Big spikes if a video hits |
| Twitter/X | 500-5k | Slow-growth thought leadership |

**Across all four**, you can absolutely hit 100k+ total followers and millions of monthly impressions in year 2, if you're consistent and the niche is right. But the real win is the **traffic** these impressions drive to your KDP listings.

### Will not be automated

- **Engagement automation** (auto-liking, auto-commenting, auto-following). Every major platform bans accounts that do this — usually within 7-14 days. The tool will not do it. You can engage manually 5-10 min/day if you want.
- **Direct posting via APIs**. Pinterest, Instagram, TikTok, and Twitter all require app approval (1-4 weeks each), and some have monthly fees. The friction isn't worth it for a one-person operation. Their **native schedulers are free and good** — see below.

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

Pin styles rotate across 4 templates (bold headline, quote, tip, listicle). Palettes are deterministic per niche so your feed looks coherent.

---

## One-time setup

If you've already run `bash setup.sh` for the video tool or KDP tool, **you're done.** Same `.venv`, same `.env`.

If not:
1. `bash setup.sh` (Mac/Linux) or `setup.bat` (Windows).
2. Paste your Anthropic API key into `.env` (same key as the other tools — costs ~$0.05-$0.15 per daily run).

---

## Daily use (3 min + uploading time)

1. **Edit `social/config.yaml` once** to set your brand:
   - `brand_name`: your pen name (use the same one as `kdp/config.yaml`)
   - `niche`, `audience`, `tagline`: who and what
   - `link_in_bio`: your Amazon author URL or Linktree
   - `featured_book_dir`: optional — point at a folder in `kdp/output/` to focus the day's content on one book

2. **Run:**
   - Mac/Linux: `bash social/run_social.sh`
   - Windows: double-click `social/run_social.bat`

3. **Open the output folder**, preview, and upload to each platform.

---

## Upload workflow (30-40 min/day, can be batched weekly)

The actual time-eating step. Each platform has a free native scheduler — use them.

### Pinterest (most important — start here)

1. Go to https://business.pinterest.com → switch your personal account to a **free business account** (one-time, ~3 min, no fee).
2. **Verify your Amazon author URL** under "Settings → Claim". This makes your pins more trusted.
3. Open your output folder. For each `01_<slug>.png` + `01_<slug>.txt` pair:
   - Click "Create" → "Create Pin"
   - Upload the PNG
   - Paste the title, description, hashtags, and destination link from the .txt
   - Click "Publish at later date" → schedule the time
4. Pinterest's free scheduler allows **100 scheduled pins at a time**. Schedule a week's worth in one sitting.
5. **Optimal cadence**: 5-10 pins per day, spread between 8am-10pm in your audience's timezone.

### Instagram

1. Go to https://business.facebook.com (Meta Business Suite) — links your IG to it for free.
2. Click "Planner" → "Create Post".
3. For each carousel folder, drag all `slide_*.png` files in order. Paste the caption from `caption.txt`.
4. For quote posts, upload the single PNG with its caption.
5. Schedule 1-2 posts per day.

### Twitter/X

1. Open each `thread_XX.txt`. Each tweet is on its own block.
2. Post tweet 1, then reply to it with tweet 2, etc.
3. **Optional**: use https://typefully.com (free for 4 scheduled posts/month) for actual scheduling.

### TikTok / Instagram Reels / YouTube Shorts

The script file has everything you need: hook + narration + on-screen captions + B-roll keywords. You have two ways to turn it into a video:

**Option A (fully automated, recommended):** use the video generator at the repo root.
1. Copy the niche from `social/config.yaml` into the top-level `config.yaml` for the video tool.
2. Run `bash run.sh`.
3. You get finished MP4s in `output/<date>/`. Upload to TikTok / Reels / Shorts.

**Option B (you on camera):** read the narration into your phone, post-process with your phone's CapCut app. ~15 min per video.

Either way, post **1 video per day**.

---

## Strategy: getting from $0 → big traffic

| Phase | What you do | Where the traffic comes from |
|---|---|---|
| **Weeks 1-4** | Pin 5-10/day, post 1 IG/day, 1 video/day, 1 thread/day. Don't read stats. | Nowhere yet — you're seeding |
| **Weeks 5-12** | Look at Pinterest analytics. Find your top 5 pins. Make 10 variants of each. Drop everything else. | Pinterest starts pushing the winners. Expect 1k-10k monthly impressions. |
| **Months 3-6** | Double down on winning angles. Add Instagram Stories with poll/question stickers (manual, 5 min/day). | Pinterest is now 50k-500k monthly impressions. Books start selling. |
| **Months 6-12** | Repurpose top Pinterest content for TikTok. Most viral pin hooks make great TikTok hooks. | Multi-platform compound. 100k-1M monthly impressions across platforms. |
| **Months 12+** | Run $5/day Pinterest Ads on your top 5 pins, $10/day Amazon Ads on the books they drive traffic to. | Paid amplification on winners only. |

The real lever is **Pinterest pin volume**. Most Pinterest creators who break out have 500-2000 pins in their library. This tool can produce 8 pins per run × daily = 240 pins per month. In a year you'll have a library that compounds.

---

## What this tool will NOT do

- Post directly to platforms (banned by ToS or requires costly approval).
- Auto-engage with other accounts (gets you banned).
- Guarantee any specific follower count or impression number.
- Replace your editorial judgment — preview every post before uploading. If a hook doesn't ring true to you, skip that pin.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ANTHROPIC_API_KEY not set` | Paste your key into `.env` at the repo root. |
| Pins all look the same | Add more palettes to `allowed_palettes` in `config.yaml`, or remove the list entirely to let the tool pick from all 8. |
| Hook quality is uneven | Run again — Claude generates fresh angles each run. Or tighten the `niche:` and `audience:` fields in the config (more specific = better hooks). |
| Pinterest rejects pins | Almost always because the destination URL doesn't match a claimed account. Claim your Amazon author page in Pinterest settings. |
| Carousel slides look cramped | Lower the `heading` length in the strategist prompt — but the tool already constrains it to 30-60 chars. If it's persistent, paste the bad output into chat and I'll fix the renderer. |

If anything errors, paste the message into the chat and I'll fix it.
