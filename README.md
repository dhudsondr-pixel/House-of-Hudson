# House of Hudson

Tooling for the House of Hudson 3D printing business: STL listing automation, customer quoting, social media content production, and faceless video generation.

This repo contains four tools that share one Python environment and one `.env`. Each is self-contained and has its own README with detailed instructions.

---

## What's in here

| Tool | Folder | What it does |
|---|---|---|
| **STL pipeline** | `stl/` | Drop an STL file in → out comes renders, cross-platform listing copy (Cults3D, MakerWorld, Printables, Thingiverse, Etsy, Patreon), recommended print settings, suggested pricing, and (optionally) a customer-facing quote PDF for print-and-ship orders. |
| **Social media factory** | `social/` | One run generates Pinterest pins, Instagram quotes + carousels, Twitter/X threads, and TikTok scripts that promote a specific STL listing or your brand. All ready to batch-schedule via Pinterest Business / Meta Business Suite. |
| **Video generator** | `/` (root) | Auto-produces vertical MP4s for YouTube Shorts / TikTok / Reels. AI script + voiceover + Pexels stock footage + on-screen captions. Configure niche in `config.yaml`. |
| **Setup** | `setup.sh` / `setup.bat` | One-time installer. Creates a venv, installs all Python deps, installs ffmpeg, creates a `.env` from the template. Run this once before anything else. |

The four tools work together but each is independently runnable. The typical flywheel:

1. Design a new STL.
2. Run `stl/run.py` → get listings + renders + suggested price.
3. Upload the STL + listings to Cults3D / MakerWorld / Printables / Etsy.
4. Point `social/config.yaml`'s `featured_design_dir:` at the STL's output folder.
5. Run `social/run.py` → get a week of pins/posts/scripts promoting that design.
6. Schedule everything via free platform schedulers.
7. (Optional) Run the video generator with a 3D-printing niche for an evergreen YouTube Shorts / TikTok channel.

---

## One-time setup

### 1. Install prerequisites

You need **Python 3** and **ffmpeg** on your computer.

- **Mac:** install [Homebrew](https://brew.sh), then run `brew install python ffmpeg`
- **Windows:** install Python from [python.org](https://www.python.org/downloads/) (tick "Add Python to PATH"), then install ffmpeg via `winget install ffmpeg` in PowerShell
- **Linux:** `sudo apt-get install python3 python3-venv python3-pip ffmpeg`

### 2. Run the setup script

```bash
bash setup.sh        # Mac/Linux
setup.bat            # Windows
```

It installs all Python dependencies into a `.venv/` folder and copies `.env.example` to `.env`.

### 3. Paste your API keys into `.env`

```
ANTHROPIC_API_KEY=sk-ant-...
PEXELS_API_KEY=...
```

- **Anthropic API key**: from https://console.anthropic.com/. Buy $10 in credit — that's enough for ~50 STL listings + ~50 social runs + ~30 videos.
- **Pexels API key**: 100% free, from https://www.pexels.com/api/. Only used by the video generator for stock footage.

---

## Daily / weekly use

Pick the rhythm that fits you. A reasonable cadence:

| When | What to run | Time |
|---|---|---|
| **Per new STL** | `bash stl/run_stl.sh` | 2-3 min compute + 15 min to upload listings to all platforms |
| **Daily (or batched 2x/week)** | `bash social/run_social.sh` | 3 min compute + 30 min to schedule pins/posts |
| **Daily (optional)** | `bash run.sh` (video generator) | 5-8 min compute + 1 min to upload each MP4 |

If you have 30-60 min/day, the highest-leverage allocation is:

- 10-15 min on `stl/` when you have a new design ready
- 30 min on `social/` (running it + scheduling its output to Pinterest in particular)
- Whatever's left on video generation OR responding to custom-order DMs from social

---

## Honest expectations

I want to be clear about what these tools can and can't do.

**What they can do:**
- Remove 30-60 min of repetitive listing/marketing work per design.
- Produce content that is on par with most mid-tier listings already on Cults3D / MakerWorld / Etsy.
- Generate enough social content to maintain a daily presence on 4 platforms.
- Help you batch-publish to platforms you'd otherwise skip (most makers only upload to 1-2 platforms because the listing work is tedious).

**What they can't do:**
- Guarantee any specific revenue.
- Replace good design — if the STL doesn't solve a real problem or look striking, no listing copy will fix that.
- Auto-engage on social media (banned by every platform; gets accounts suspended).
- Upload directly to Cults3D / MakerWorld / etc — these all want a human in the loop for uploads.

**Realistic 12-month outcomes** assuming daily use, 1-2 new STLs per week, and consistent social scheduling:

- **Cults3D + Etsy STL sales**: $100-2,000/mo (high variance by niche)
- **MakerWorld + Printables engagement points**: $50-1,000/mo equivalent (Bambu rewards program)
- **Print-on-demand custom orders from social/DM leads**: 2-15 orders/mo at your usual job rates
- **Total**: roughly $500-5,000/mo additional revenue from automated marketing on top of your existing business

The breakouts (the 10% who exceed $10k/mo) are typically the ones who (a) found a specific high-demand niche, (b) iterated based on which designs sold, and (c) reinvested into better tooling or paid ads on winners.

---

## File tree

```
House-of-Hudson/
├── README.md                     # this file
├── setup.sh / setup.bat          # one-time installer
├── .env.example                  # template; copy to .env and fill in keys
├── requirements.txt              # Python deps for all tools
├── config.yaml                   # video generator config
├── run.py / run.sh / run.bat     # video generator entry points
├── src/                          # video generator source
│
├── stl/
│   ├── README.md                 # STL pipeline docs
│   ├── config.yaml               # STL pipeline config
│   ├── run.py / run_stl.sh/.bat  # STL pipeline entry points
│   ├── input/                    # drop your STL folders here
│   ├── output/                   # generated listings land here (gitignored)
│   └── src/                      # STL pipeline source
│
└── social/
    ├── README.md                 # social factory docs
    ├── config.yaml               # social factory config
    ├── run.py / run_social.sh/.bat
    ├── output/                   # generated posts land here (gitignored)
    └── src/                      # social factory source
```

---

## Troubleshooting

Each tool's README has a Troubleshooting section. Common issues across all three:

| Problem | Fix |
|---|---|
| `ANTHROPIC_API_KEY not set` | You haven't pasted your key into `.env` yet. |
| `ffmpeg not found` | Run setup.sh or install ffmpeg manually (see step 1 above). |
| Topic / listing / plan generation fails | Anthropic account is out of credit. Top up at https://console.anthropic.com/billing. |

If anything errors, paste the message and I'll fix it.
