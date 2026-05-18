# House of Hudson — Faceless Short-Form Video Generator

A program that writes, voices, and assembles short-form videos (YouTube Shorts / TikTok / Reels) for you. You run it, you upload the MP4s, you keep doing that, and — *with consistency and luck* — a channel grows.

---

## The honest expectations

**No program can guarantee $1000/month. Anyone who tells you otherwise is lying.** What this program *does* is remove every part of video creation except the click-to-upload step. The actual income depends on:

- **Consistency** — most successful faceless channels post 1+ video per day for 60-90 days before anything takes off.
- **Niche & hook quality** — the niche in `config.yaml` matters enormously. Pick something with proven demand (history, psychology, space, weird animals) over something obscure.
- **Luck** — short-form algorithms are stochastic. A channel might do nothing for 40 videos and then one hits 2M views.
- **Monetization path** — YouTube Shorts pays via the YouTube Partner Program once you hit 1k subs + 10M Shorts views in 90 days. TikTok pays via the Creator Rewards Program at 10k followers. Until then, income comes from affiliate links in your bio, course/Gumroad funnels, or sponsorships.

**Realistic 90-day outcomes for someone posting daily:** 70% earn $0, 20% earn $50-500/mo, 10% earn $1k+/mo. This tool gives you the cheapest possible shot at being in the last two buckets.

---

## What it does

Each time you run it, the program:

1. Asks Claude to brainstorm fresh topic ideas in your chosen niche.
2. Writes a short, hook-first script for each topic.
3. Generates AI voiceover (free Google TTS).
4. Pulls matching stock video clips from Pexels (free API).
5. Assembles a vertical MP4 with captions burned in.
6. Saves the MP4s plus a `captions.txt` file with ready-to-paste descriptions/hashtags.

You upload. That's it.

---

## One-time setup (~10 minutes)

### Step 1: Install prerequisites

You need **Python 3** and **ffmpeg** on your computer.

- **Mac:** install [Homebrew](https://brew.sh), then run `brew install python ffmpeg`
- **Windows:** install Python from [python.org](https://www.python.org/downloads/) (tick "Add Python to PATH" during install), then install ffmpeg via `winget install ffmpeg` in PowerShell
- **Linux:** `sudo apt-get install python3 python3-venv python3-pip ffmpeg`

### Step 2: Get your API keys

You need two — one paid (cheap), one free.

| Service | Cost | Sign-up link |
|---|---|---|
| **Anthropic (Claude)** | ~$0.01-$0.05 per video generated. Add $5 of credit and it'll last weeks. | https://console.anthropic.com/ |
| **Pexels** | 100% free, forever. Just sign up. | https://www.pexels.com/api/ |

For each, sign up, find the "API Keys" page, and copy your key somewhere safe.

### Step 3: Run setup

In a terminal, inside this folder:

- **Mac / Linux:** `bash setup.sh`
- **Windows:** double-click `setup.bat`

The script will install everything and create a `.env` file.

### Step 4: Paste your API keys

Open the file called `.env` in any text editor (Notepad works). You'll see:

```
ANTHROPIC_API_KEY=sk-ant-...
PEXELS_API_KEY=
```

Replace the placeholder with your real Anthropic key, and paste your Pexels key after the `=`. Save the file.

### Step 5 (optional): Pick your niche

Open `config.yaml`. Change the `niche:` line to whatever channel you want to make. The file has several examples commented out — pick one or write your own.

**Strong starter niches** (proven to work for faceless channels):
- "fascinating historical facts most people never learned in school"
- "weird psychology facts about human behavior"
- "strange unsolved mysteries from around the world"
- "mind-blowing space facts and discoveries"

**Don't:** keep changing your niche. Pick one and post 30 videos in it before you reconsider.

---

## Daily use

Once setup is done, every time you want new videos:

- **Mac / Linux:** `bash run.sh`
- **Windows:** double-click `run.bat`

That's the one command. It takes 3-8 minutes to make 3 videos. They land in `output/<today's-date>/`, along with a `captions.txt` containing the description and hashtags to paste when you upload.

### Recommended workflow

1. Run the program in the morning.
2. Open the output folder.
3. Watch each MP4 (10 seconds each — skip any that look wrong).
4. Upload to **one platform consistently** (don't spread thin — pick YouTube Shorts OR TikTok and focus). Paste the description from `captions.txt`.
5. Post at the **same time every day**. Algorithms reward this.
6. Don't read your stats for the first 30 days. Just post.

---

## Tuning for results

After 10-20 videos, look at which got the most views. In `config.yaml`:

- If the videos look choppy → lower `videos_per_run` to 1, increase `target_seconds` for richer scripts.
- If the voice sounds wrong → try a different `voice` setting.
- If you want a different visual style → change `niche` to something more visually concrete ("deep sea creatures" gives better stock footage than "philosophical paradoxes").

---

## Going from $0 → revenue

This tool produces the supply. Demand (views) and monetization are still on you. The lowest-friction monetization paths, in order of how soon they pay:

1. **Affiliate links in bio** — pick one Amazon/affiliate product relevant to your niche, drop the link in your YouTube / TikTok bio from day one. ~$0-100/mo with small channels.
2. **YouTube Partner Program (Shorts)** — needs 1k subs + 10M Shorts views in 90 days. Pays roughly $0.05/1k views on Shorts.
3. **Gumroad/course funnel** — once you have 5k+ followers, sell a $7 ebook/template tied to your niche. This is where most $1k+/mo creators get there.
4. **Sponsorships** — at 50k+ followers.

The tool does steps 1-N of content creation. You do the upload + the bio link + the consistency.

---

## What this tool is NOT

- ❌ A get-rich scheme. If you post 5 videos and quit, you'll earn nothing. Same as any business.
- ❌ A way to upload directly to TikTok/YouTube from code. Both platforms ban automation. You upload manually — this is a feature, not a bug. It keeps your account safe.
- ❌ Magic. The script-writing quality is good but not perfect. Watch each video before posting.

## What you can change later

- Swap `gTTS` for **ElevenLabs** (better voice, ~$5/mo) by editing `src/voice.py`.
- Swap stock footage for **AI-generated images** (Stable Diffusion / Replicate) by editing `src/footage.py`.
- Add a **scheduler** (cron / Task Scheduler) so videos generate every morning without you opening anything.

If you don't want to touch the code, the defaults are fine. Just run, upload, repeat.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ffmpeg not found` | See Step 1 above. The setup script will install it on Mac/Linux. |
| `ANTHROPIC_API_KEY not set` | You didn't fill in `.env`. Open it and paste your keys. |
| Topic brainstorm fails | Usually means your Anthropic account has no credit. Add $5 at https://console.anthropic.com/ |
| Stock clips all look weird | Your niche is too abstract. Change `niche:` to something more concrete and visual. |
| Videos sound robotic | gTTS is free but basic. Upgrade to ElevenLabs (see "What you can change"). |

If you get stuck, paste the error message into the chat with me and I'll fix it.
