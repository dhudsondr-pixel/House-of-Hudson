# House of Hudson

Two projects live here:

1. **`etsy_planner_factory/`** — a one-click generator that produces 36
   ready-to-sell Etsy printable-planner listings (PDFs, mockup images, and
   SEO-tuned listing copy). **Start here:** see [`SETUP.md`](./SETUP.md) for
   the no-coding-knowledge guide.
2. **`bambu_optimizer/`** — a separate CLI that recommends Bambu Lab 3D
   printer settings. See below.

---

# Bambu Print Settings Optimizer

A CLI that picks Bambu Studio settings for the **A1, H2D, H2C, P2S, and X2D**
based on filament, nozzle size, and what the part is for.

> Of the listed printers, A1 and H2D have verified profiles. H2C, P2S, and X2D
> are placeholders — they print a warning. Edit `bambu_optimizer/printers.py`
> with the real specs once available.

## Use it

```bash
# Interactive wizard
python -m bambu_optimizer

# One-shot
python -m bambu_optimizer --printer H2D --material PA-CF \
    --quality fine --purpose mechanical --overhangs

# Same job, every printer side-by-side
python -m bambu_optimizer --material PETG --purpose functional --compare-all

# Paste-ready Bambu Studio overrides
python -m bambu_optimizer --printer A1 --material PLA --format studio
```

## Inputs

- `--printer`: A1, H2D, H2C, P2S, X2D
- `--material`: PLA, PLA+, PETG, ABS, ASA, PC, PA, PA-CF, PETG-CF, TPU
- `--nozzle`: 0.2, 0.4, 0.6, 0.8 (mm)
- `--quality`: draft, standard, fine, ultrafine
- `--purpose`: visual, functional, mechanical, miniature, prototype
- Flags: `--overhangs --bridges --tall-narrow --fine-detail --watertight --transparent --annealed --outdoor`

## What it computes

Layer height, line width, wall/top/bottom counts, infill % and pattern,
nozzle/bed/chamber temps, per-feature speeds, volumetric-flow cap, fan curves,
retraction, supports (with dual-extruder dissolvable interfaces on H2D),
brim, ironing, adaptive layers, plus rationale and warnings.

## Layout

```
bambu_optimizer/
    printers.py     # printer capability profiles
    materials.py    # filament profiles
    optimizer.py    # recommendation engine
    render.py       # text / JSON / Studio override formatters
    cli.py          # argparse + interactive wizard
tests/
    test_optimizer.py
```

## Tests

```bash
python -m unittest discover tests -v
```
