# How to use the Etsy Printable Planner Factory

This guide assumes you've never written code. Follow the steps in order.

---

## Step 1 — Install Python (5 minutes, one time only)

Python is the free software that runs the factory.

**On Windows:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button.
3. Run the installer. **IMPORTANT:** check the box that says
   *"Add Python to PATH"* at the bottom of the first screen.
4. Click "Install Now". Wait for it to finish.

**On Mac:**
1. Open the **Terminal** app (press Cmd+Space, type "Terminal", press Enter).
2. Paste this line and press Enter:
   ```
   xcode-select --install
   ```
   If it says "already installed", that's fine.
3. Python 3 comes with macOS. You're done.

---

## Step 2 — Run the factory

**On Windows:** double-click `run.bat`.

**On Mac:**
1. Open Terminal (Cmd+Space → "Terminal").
2. Drag the folder this file is in onto the Terminal window — it'll paste the path.
3. Type `cd ` (with a space), then paste, then press Enter.
4. Type `./run.sh` and press Enter.

The first run installs two free libraries (`reportlab`, `Pillow`) — this
takes about 30 seconds. After that, generation takes under a minute.

When it's done, you'll see a new folder called **`output/`** with 36
subfolders, one per listing. Each subfolder contains:

```
product.pdf          <- the file your customer downloads after buying
image-1-hero.png     <- Etsy listing photo #1 (must be square, this is 2000x2000)
image-2-preview.png  <- Etsy listing photo #2 (a sample page mockup)
image-3-card.png     <- Etsy listing photo #3 (what's included)
listing.txt          <- your title, tags, description, and suggested price
```

---

## Step 3 — Create an Etsy seller account (15 minutes, one time)

1. Go to https://www.etsy.com/sell
2. Click "Get started" and fill in the form. You'll need:
   - A photo or logo for your shop
   - A bank account for payouts
   - A debit/credit card for fees (Etsy charges $0.20 per listing,
     plus ~6.5% per sale)
3. Pick a shop name. Suggestions: something with "Studio", "Co", "Press",
   "Goods", "Paper". Avoid your real name if you want it to feel like a brand.
4. Set your shop to sell **digital downloads**. When asked what you make,
   choose "I make it myself" → "Digital file".

---

## Step 4 — Upload your first listing (5 minutes per listing)

1. Pick one folder inside `output/`. We'll use
   `daily-planner__minimalist-mono` as the example.
2. In Etsy: click your shop → **Listings** → **Add a listing**.
3. Photos: drag in `image-1-hero.png`, `image-2-preview.png`,
   `image-3-card.png` (in that order — first one is the cover).
4. Open `listing.txt` in the same folder. Copy/paste:
   - The **TITLE** line into Etsy's "Listing title" field.
   - The **PRICE** number into the "Price" field.
   - Each of the **13 tags** into Etsy's tag fields (one per box, no commas).
   - The **DESCRIPTION** block into Etsy's "Description" field.
5. Under "Type", select **Digital file**.
6. Upload **`product.pdf`** as the digital file.
7. Hit **Publish**.

Repeat for as many listings as you have time for.

---

## Step 5 — Daily routine (your 30 minutes/day)

**Each weekday morning, do this in any order:**

1. **Upload 3–5 new listings** (about 15–20 min). Cycle through the 36
   folders. Once you've uploaded all 36, re-run `run.py` — the factory is
   deterministic but you can swap planner content/themes in the code
   later, or hand-edit a few to add variety.
2. **Reply to any Etsy messages** (about 5 min). Etsy heavily favors
   shops that reply within 24 hours.
3. **Check sales** (about 5 min). Note which listings get views and which
   convert. Double down on the themes that work.

That's it. No physical shipping. Etsy auto-delivers the PDF when someone buys.

---

## Realistic expectations

- **Month 1:** $0 – $50. Etsy uses your first 2–4 weeks of sales as a
  trust signal; new shops rank low.
- **Month 2–3:** $50 – $300, if you keep uploading.
- **Month 4–6:** $300 – $1,000+ is achievable with ~150 active listings
  and decent themes.
- **Beyond month 6:** depends entirely on whether you keep listing,
  refresh stale ones, and respond to reviews.

Things that **kill** this business model:
- Uploading once and never coming back. The algorithm penalizes inactive
  shops hard.
- Ignoring messages.
- Copying another seller's exact listing wording (Etsy detects this).
- Using AI-generated descriptions verbatim without personalizing your
  shop's "voice" — Etsy is starting to penalize obvious AI listings.
  The descriptions in `listing.txt` are starting points; tweak the
  intro line on each one.

---

## When it stops being worth it

If after **90 days of 5 listings/day** (so 450+ listings live) you're
under $100/month total, the niche is probably saturated. Options:
- Switch from planners to **resume templates** or **wedding stationery**
  (higher prices, less competition, but I haven't built those generators
  yet — ask me to).
- Move to Gumroad/Payhip instead (no listing fees, but you have to drive
  your own traffic).
- Call it a failed experiment. You'll be out ~$10 in Etsy fees.
