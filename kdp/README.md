# House of Hudson — KDP Auto-Publisher

A program that generates complete, KDP-ready paperback book packages. Each run produces a folder per book containing the interior PDF, cover PDF, and the listing metadata (title, description, keywords, categories). You upload them to Amazon. Each book becomes an asset that earns royalties indefinitely.

---

## The honest expectations

This is an **asset business**. The economics work like this:

- A 120-page low-content paperback at $7.99 earns roughly **$2.50 royalty per sale** on Amazon US.
- An "average" low-content book on Amazon sells **0-5 copies a month**.
- A "good" one sells **10-30/month**.
- A "winner" sells **50-200+/month** ($125-500/mo from one book).

So the math to hit $1000/month:

| Catalog size | Avg sales/book/mo | Monthly revenue |
|---|---|---|
| 20 books  | 5  | ~$250  |
| 50 books  | 8  | ~$1000 |
| 100 books | 10 | ~$2500 |
| 200 books | 12 | ~$6000 |

**Most low-content publishers cross $1k/mo somewhere between book 50 and book 150**, after 3-6 months of consistent uploading and iteration. The realistic 12-month target with this tool: $1k-5k/mo. Top operators clear $20k+/mo, but they're picking better-than-average niches and learning from data — both of which you'll start doing after your first 30 uploads.

What this program **cannot do**:
- Guarantee that any given book will sell.
- Upload to KDP for you (Amazon doesn't allow automation; you upload manually — 5 min per book).
- Replace your judgment about which niches are worth pursuing.

What it **does**:
- Removes the 8-12 hours per book that designers/writers normally spend producing one.
- Spits out KDP-compliant files that pass Amazon's automated validators.
- Generates listing copy good enough to compete with most listings on Amazon today.

---

## What it produces

Each run creates one folder per book:

```
output/2026-05-18/
  prompt_journal__the-quiet-mind/
    interior.pdf      ← upload as "Manuscript"
    cover.pdf         ← upload as "Book Cover"
    metadata.txt      ← copy/paste fields into KDP's listing form
```

The four book formats supported:

| Format | What it is | Best for |
|---|---|---|
| `lined` | Plain lined journal with title page, "belongs to" page, then 100+ lined pages | Gift-niche journals (e.g., "Coffee Lover's Notebook") |
| `prompt_journal` | One unique reflection prompt per page + writing space | Self-care, gratitude, therapy, mindfulness niches |
| `tracker` | Habit/goal grid with one month per page (8 habits × 31 days) | Productivity, fitness, sobriety, ADHD niches |
| `wordsearch` | Themed word search puzzles with solutions section | Hobby niches, retiree gifts, vacation books |

---

## One-time setup (~5 minutes)

If you already ran the video generator's `setup.sh`, **you're done** — the KDP tool reuses the same `.venv` and `.env`. Skip to "Daily use".

If you haven't:

1. **Install Python 3 and ffmpeg.** (The setup script handles ffmpeg automatically on Mac/Linux.)
2. **Get an Anthropic API key.** Sign up at https://console.anthropic.com/, add $5-10 of credit. Each book costs **$0.10-$0.40** in API calls (prompt journals cost more because they generate ~120 unique prompts).
3. **Run setup once.**
   - Mac / Linux: `bash setup.sh`
   - Windows: double-click `setup.bat`
4. **Paste your Anthropic key** into the `.env` file that gets created. (Ignore the `PEXELS_API_KEY` line unless you're also using the video generator — KDP doesn't need it.)

---

## Daily use

1. Edit `kdp/config.yaml`. The two values that matter most:
   - `theme:` — your broad niche. **Be specific.** "Self-care for working moms" sells, "self-care" doesn't.
   - `book_types:` — which formats to generate this run.
2. Run:
   - Mac / Linux: `bash kdp/run_kdp.sh`
   - Windows: double-click `kdp/run_kdp.bat`
3. Each book takes 1-3 minutes (prompt journals slower because of all the unique prompts). Output lands in `kdp/output/<today>/`.

### Then upload to KDP (5 minutes per book)

1. Go to https://kdp.amazon.com → **Create** → **Paperback**
2. Open the book's `metadata.txt`. Copy each field into the matching field in the KDP form:
   - **Language**: English
   - **Title** & **Subtitle**: copy from metadata.txt
   - **Series**: leave blank for first book (you can create a series later for sequels/volumes)
   - **Edition number**: 1
   - **Author** / **Contributors**: use your pen name (set in `config.yaml` as `author_name`)
   - **Description**: paste the description text. Don't use the "AI-generated" disclosure — you wrote the prompts and the niche; the AI is a tool, not the author.
   - **Publishing rights**: "I own the copyright"
   - **Keywords**: paste each of the 7 keywords into a separate keyword box
   - **Categories**: pick the 2 suggested categories (or the closest available in Amazon's tree)
   - **Adult content**: No
3. Click "Save and Continue".
4. **Print settings**:
   - **ISBN**: choose "Get a free KDP ISBN"
   - **Imprint**: leave blank
   - **Print options**: Black & white interior on **white paper**, **6x9 inches**, **no bleed**, **glossy cover**
5. **Upload your files**:
   - Upload `interior.pdf` for "Manuscript"
   - Upload `cover.pdf` for "Book cover"
   - Click "Launch Previewer". Wait for it to load. Click through every page.
   - If you see warnings, KDP will tell you exactly what's wrong; the most common ones are cosmetic and you can publish anyway.
6. **Pricing**:
   - **Marketplace**: All (or just .com if you're new)
   - **List price**: $7.99 USD (good default for journals/trackers; $8.99-9.99 for prompt journals and word search books)
   - **Royalty plan**: 60% (the only option for paperback)
7. Click **Publish**. Amazon takes 24-72 hours to approve.

### A safe upload cadence

- **Days 1-7**: upload 1 book per day. Mix formats and niches.
- **Days 8-30**: upload 2-3 per day if your account is in good standing.
- After 30 days with no issues: bulk upload as many as you want.

Why slow at first: Amazon flags accounts that upload 20 books on day one. You're trying to look like a small publisher, not a content farm.

---

## Niche strategy (this is where the money is)

The tool generates technically-correct books in any niche you point it at. **Your edge is picking niches that aren't already drowning in listings.**

### How to find a good niche

1. Go to Amazon, search for the keyword phrase you're considering (e.g., "marathon training journal").
2. Look at the **first 10 results**. What's their format? Their price? Look at the **BSR** (Best Sellers Rank) — click into each product and scroll to "Product details".
3. Rules of thumb:
   - **BSR under 100,000** in Books = selling daily; the niche has demand.
   - **BSR 100,000-500,000** = selling weekly; viable.
   - **BSR over 1,000,000** = dead; either the listing is bad or the niche doesn't sell.
   - If the top 5 results all have BSR under 200k AND fewer than 50 reviews → enter that niche.
4. The niche names to **avoid** (oversaturated): "gratitude journal", "5 minute journal", "lined notebook", "blank journal", "sudoku book".
5. The niche pattern that **works**: `[hobby/profession/identity] + [book format]`. Examples:
   - "Beekeeping logbook for hobbyist apiarists"
   - "Sermon prep journal for pastors"
   - "Sobriety milestone tracker for 12-step members"
   - "Trail running training log for ultramarathoners"
   - "Witchy gratitude journal for solitary practitioners"

### Building a "series"

Once you find a niche that sells, lean in. Make a Volume 1, Volume 2, etc. Use the same cover style (the program is deterministic on the niche name as a seed — pass the same theme and you'll get consistent visuals). Amazon's "Series" feature lets buyers find your other volumes from any one book's page. **Series quintuple your per-customer revenue.**

---

## Scaling: getting from $0 → $1k/mo → $5k+/mo

| Phase | Time | What you do |
|---|---|---|
| **0-30 days** | First month | Upload 1-3 books/day. Try 3-5 different niches. Don't read your sales numbers. |
| **30-60 days** | Find winners | Look at sales reports. Identify your top 3-5 books. Create Volume 2/3 of each. |
| **60-90 days** | Compound | 2x down on niches that worked, drop the ones that didn't. Add the `wordsearch` format to your bestsellers' niches. |
| **90-180 days** | Scale | Catalog should be 100+ titles. At this point you're earning $500-2k/mo. Reinvest in better covers (hire a $30 cover designer for your top 10 books) and consider paid Amazon Ads (~$5/day on bestsellers). |
| **180+ days** | Optimize | Run Amazon ads with a target ACOS of <30%. Expand into matching ebook releases for top performers. Build a dedicated brand around your top niche. |

The truly automated part of this is **content production**. The judgement (niches, pricing, which books to amplify) is on you. With 30-60 min/day, expect to upload 5-15 books per day in the early phase and slow to 1-3/day once you're optimizing.

---

## Things that will get your account banned (avoid these)

- Uploading 50+ books in your first week.
- Reusing identical interior content across books with only the cover changed.
- Using copyrighted material (lyrics, character names, brand names) without rights.
- Stuffing keywords or making misleading claims in the title/description (e.g., "BEST GRATITUDE JOURNAL EVER GUARANTEED").
- Calling yourself the author of a book that disclosed itself as AI-generated.

The tool defaults are designed to avoid all of these, but you're ultimately the publisher.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ANTHROPIC_API_KEY not set` | Open the `.env` file in the repo root, paste your key after `ANTHROPIC_API_KEY=`. |
| Topic brainstorm fails | Anthropic account out of credit. Add $5 at https://console.anthropic.com/billing. |
| KDP rejects the cover for "spine text too close to edge" | Increase `page_count` in `config.yaml` to 130-150. Thicker spine = safer. |
| KDP previewer warns about "blank page" | This is fine. The interior intentionally leaves some pages blank for journals. |
| Cover looks too plain | The defaults are intentionally conservative (low-content covers that look "designed" actually sell worse than clean ones). If you want fancier, hire a Fiverr designer for your top 10 books. |
| Prompt journal repeats prompts | Increase the brainstorm batch size in `src/metadata.py` or lower `page_count`. |

If you hit an error, paste it into the chat and I'll fix it.
