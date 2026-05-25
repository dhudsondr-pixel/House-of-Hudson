# House of Hudson — STL Listing & Quote Pipeline

A program that takes an STL file and produces everything you need to **sell that design** as a digital download AND **quote it** as a print-and-ship custom order.

For each design folder you drop into `stl/input/`, one run produces:

- **Renders** (PNG): three preview angles of the model
- **Cross-platform listing copy**: ready-to-paste text for Cults3D, MakerWorld, Printables, Thingiverse, Etsy digital, and a Patreon announcement post
- **Print settings** recommendation: layer height, infill, supports, orientation, material
- **STL pricing** suggestions per platform
- **Print-on-demand quote PDF** (optional): a customer-facing PDF with specs, breakdown, and total

---

## What it doesn't do

- Doesn't upload files anywhere (Cults / MakerWorld / Printables / Thingiverse / Etsy all want a human in the loop or require app approval — you still upload manually, ~3-5 min per platform).
- Doesn't slice the STL or generate true G-code timing. The print-time and weight numbers are **heuristic estimates** based on volume, bounding box, and infill — good enough to quote a customer or set expectations, but always verify by slicing in PrusaSlicer / Bambu Studio / OrcaSlicer before printing for real.
- Doesn't reach inside an STL to fix bad meshes — if `analysis.txt` says "Watertight: NO", run it through a mesh repair tool (Microsoft 3D Builder, Meshmixer, Bambu Studio's repair) before quoting.

---

## How to use

### One-time setup

Same as the rest of the repo. If you've already run `bash setup.sh` once, you're done.

```bash
bash setup.sh        # Mac/Linux  (installs Python deps + ffmpeg)
setup.bat            # Windows
```

Then paste your Anthropic API key into `.env` at the repo root. ~$0.05-$0.20 per design in API costs depending on how much description you provide.

### Daily use

**Step 1: drop your STL in.**

For each design you want to list or quote:

```
stl/input/<design-name>/
    your_file.stl          (or .3mf or .obj)
    description.txt        (optional — one paragraph: what it is, who it's for, why someone wants it)
    customer.yaml          (optional — only if this is a custom-order quote)
```

The `description.txt` is the most important file. The richer your one paragraph, the better the listings. Example:

```
Modular cable tray for under-desk routing. Snap-together 100mm segments with
optional aluminium-extrusion mounting clips. Designed for standing desks where
cables need to flex when the desk moves. PETG recommended for heat resistance
near power bricks. No supports needed in the orientation provided.
```

For a customer quote, add `customer.yaml`:

```yaml
name: "Jane Smith"
email: "jane@example.com"
notes: "Wants 4 of these in matte black PETG. Pickup in Portland."
```

**Step 2: run it.**

```bash
bash stl/run_stl.sh        # Mac/Linux
stl/run_stl.bat            # Windows
```

**Step 3: review and publish.**

Each design produces a folder in `stl/output/<today>/<design-name>/`:

```
analysis.txt             # dimensions, volume, weight, time
render_iso.png           # use as the hero listing image
render_front.png
render_top.png
listing_cults3d.txt      # paste into Cults3D's upload form
listing_makerworld.txt
listing_printables.txt
listing_thingiverse.txt
listing_etsy.txt
patreon_post.txt
print_settings.txt
stl_pricing.txt
quote.pdf                # only if customer.yaml was provided
```

Open each `listing_*.txt`, copy the fields, paste into each platform's upload form. Use the renders as the cover image plus your own printed-product photos when you have them.

---

## Configuration

Edit `stl/config.yaml` once:

- **Pricing**: `filament_cost_per_kg`, `machine_rate_per_hour`, `labor_rate_per_hour`, `markup_pct` — these drive the quote PDF totals.
- **Render style**: `studio_white`, `midnight`, `blueprint`, `industrial`, `soft_pastel`, or `neon` — pick what matches your brand.
- **Material**: default `PLA`. Used for weight + time estimates.
- **License**: how you grant rights for the digital file.

---

## Platform notes (worth knowing before you upload)

| Platform | Revenue model | Approval delay | Notes |
|---|---|---|---|
| **Cults3D** | Direct sales, 80% to you | Instant | Best margins. Strong organic search if title/tags are good. |
| **MakerWorld** | Free uploads + Bambu pays via "engagement points" | Instant | Bambu printer owners are HUGE buyers. Top creators net $500-5k/mo on points alone. |
| **Printables** | Free + Prusa "club points" → Prusament filament + cash | Instant | Smaller revenue, but the community is high quality. |
| **Thingiverse** | Free; some indirect revenue from related Etsy traffic | Instant | Legacy platform, still has great SEO. Worth uploading even for free. |
| **Etsy (digital)** | Direct sales | Account approval (~1 day) | Etsy buyers often don't own a printer. If you offer print-and-ship, mention it in the description. |
| **Patreon** | Monthly subs from your patron tiers | Instant | Use the generated patreon_post.txt to announce each new STL to existing patrons. |

**Recommended workflow for a new design:**

1. Upload free everywhere (MakerWorld, Printables, Thingiverse) to maximize discovery and rack up engagement points.
2. Charge for it on Cults3D and Etsy (slightly different pricing — Etsy buyers pay more).
3. Wait a week, look at which platform drove most downloads/sales, lean into that one for your next design.

---

## Realistic expectations

Selling STLs is a **portfolio game**. Most individual designs earn $10-$200 lifetime on Cults3D. The breakouts are the ones that solve a specific problem people search for (e.g., "Bambu A1 spool holder", "headphone hook for monitor arm"). You typically need 30-60 listings before any one of them hits.

Realistic 12-month revenue with 1-2 new designs per week and consistent cross-platform uploads: $200-2k/month from STL sales + whatever your print-on-demand orders contribute.

The tool removes the 30-45 minutes of writing/photographing per design. The design quality and niche selection are still on you.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Watertight: NO` in analysis.txt | Open the STL in Bambu Studio or Microsoft 3D Builder, use "Repair mesh", export the fixed file. |
| Renders look low-poly (visible triangles) | Your source STL is low-poly. Re-export at higher detail from Fusion / Blender. The tool just renders what you give it. |
| Print time estimate way off vs. slicer | The estimate is heuristic. For accurate timing, slice the STL in your actual slicer with your actual profile and use that number. |
| Listing copy mentions wrong material | Edit `default_material:` in config.yaml. |
| Etsy copy doesn't mention print service | Set `offers_print_service: true` in config.yaml. |
