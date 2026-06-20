# House of Hudson

Two projects live here:

1. **`etsy_planner_factory/`** — a one-click generator that produces 36
   ready-to-sell Etsy printable-planner listings (PDFs, mockup images, and
   SEO-tuned listing copy). **Start here:** see [`SETUP.md`](./SETUP.md) for
   the no-coding-knowledge guide.
2. **`bambu_optimizer/`** — a separate CLI that recommends Bambu Lab 3D
   printer settings. See below.
3. **`bubble_letter_factory/`** — generates 26 puffy bubble-letter STLs for
   3D printing (`python -m bubble_letter_factory`).
4. **`lithophane_frame_factory/`** — turns any photo into a 3D-printable
   *framed lithophane*. See below.

---

# Lithophane Frame Factory

Turn a photo into a **framed lithophane** — a thin translucent panel whose
thickness tracks image brightness, so the picture only appears when light
shines through it from behind. A raised border frames the image; the back is
flat, so it prints on a Bambu with **no supports**.

## Use it

```bash
# Built-in demo set (no photos needed) -> STLs + backlit previews
python -m lithophane_frame_factory

# Your own photos (any folder, or a single file)
python -m lithophane_frame_factory --input ./my-photos

# One photo, bigger panel + chunkier frame
python -m lithophane_frame_factory --input cat.jpg \
    --width 140 --frame-width 12 --max-thickness 3.4
```

Outputs land in `output-lithophanes/`: one `.stl` per image plus a
`*_backlit.png` showing how it looks lit. The bulky STLs are git-ignored
(they regenerate in seconds and are usually made per customer photo); the
small preview PNGs are committed as a browsable gallery.

## Key options

- `--width` image-area width in mm (frame adds more); `--pitch` XY detail
- `--min-thickness` / `--max-thickness` wall range (bright→thin, dark→thick)
- `--frame-width` / `--frame-depth` border size and stand-off
- `--gamma` midtone contrast when backlit; `--invert` for negatives
- `--faces` cap mesh face count; `--no-preview` skip PNGs

## How it works

The image becomes a thickness map (Beer-Lambert: dark = thick = blocks light)
embedded inside a taller frame border. Frame + image are emitted as a single
watertight heightmap solid with a flat back — no boolean unions, so no
OpenSCAD/Blender/manifold backend is required.

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
