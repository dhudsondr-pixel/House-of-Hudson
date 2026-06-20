"""Command-line interface for the lithophane frame factory.

    # Built-in demo set (no photos needed) -> STLs + backlit preview
    python -m lithophane_frame_factory

    # Your own photos (any folder of jpg/png) into framed lithophanes
    python -m lithophane_frame_factory --input ./my-photos

    # One photo, bigger panel, chunkier frame, darker max thickness
    python -m lithophane_frame_factory --input cat.jpg \
        --width 140 --frame-width 12 --max-thickness 3.4
"""

import argparse
import re
from pathlib import Path

from PIL import Image

from .generate import SAMPLE_SCENES, LithophaneSpec, build_one
from .preview import backlit_image, contact_sheet


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "image"


def _gather_inputs(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    raise SystemExit(f"Input path not found: {path}")


def build_spec(name: str, args: argparse.Namespace) -> LithophaneSpec:
    return LithophaneSpec(
        name=name,
        image_width_mm=args.width,
        pixel_pitch_mm=args.pitch,
        min_thickness_mm=args.min_thickness,
        max_thickness_mm=args.max_thickness,
        frame_width_mm=args.frame_width,
        frame_depth_mm=args.frame_depth,
        gamma=args.gamma,
        invert=args.invert,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="lithophane_frame_factory",
        description="Turn photos into 3D-printable framed lithophanes.",
    )
    ap.add_argument("--input", "-i", type=Path,
                    help="image file or folder of images (default: built-in demos)")
    ap.add_argument("--output", "-o", type=Path,
                    help="output folder (default: ./output-lithophanes)")
    ap.add_argument("--width", type=float, default=100.0,
                    help="image area width in mm (default 100)")
    ap.add_argument("--pitch", type=float, default=0.3,
                    help="XY pixel pitch in mm; smaller = more detail (default 0.3)")
    ap.add_argument("--min-thickness", type=float, default=0.8,
                    help="thinnest wall in mm, bright areas (default 0.8)")
    ap.add_argument("--max-thickness", type=float, default=3.0,
                    help="thickest wall in mm, dark areas (default 3.0)")
    ap.add_argument("--frame-width", type=float, default=8.0,
                    help="frame border width in mm (default 8)")
    ap.add_argument("--frame-depth", type=float, default=4.5,
                    help="frame stand-off depth in mm (default 4.5)")
    ap.add_argument("--gamma", type=float, default=1.6,
                    help="midtone contrast boost when backlit (default 1.6)")
    ap.add_argument("--invert", action="store_true",
                    help="invert brightness (for negatives / X-ray look)")
    ap.add_argument("--faces", type=int, default=0,
                    help="cap mesh face count (0 = no decimation)")
    ap.add_argument("--no-preview", action="store_true",
                    help="skip writing backlit preview PNGs")
    args = ap.parse_args(argv)

    out_dir = args.output or Path.cwd() / "output-lithophanes"
    faces = args.faces or None

    jobs: list[tuple[str, Image.Image | None]] = []
    if args.input:
        for p in _gather_inputs(args.input):
            jobs.append((_slug(p.stem), Image.open(p)))
    else:
        jobs = [(scene, None) for scene in SAMPLE_SCENES]

    if not jobs:
        raise SystemExit("No images found to process.")

    print(f"Generating {len(jobs)} framed lithophane(s) -> {out_dir}\n")
    for name, img in jobs:
        spec = build_spec(name, args)
        stl = build_one(spec, out_dir, img=img, target_face_count=faces)
        kb = stl.stat().st_size // 1024
        line = f"  {name:<18} {stl.name}  ({kb:>5} KB)"
        if not args.no_preview:
            prev = backlit_image(spec, img=img)
            prev_path = out_dir / f"lithophane_{name}_backlit.png"
            prev.save(prev_path, "PNG", optimize=True)
            line += f"  + {prev_path.name}"
        print(line)

    if not args.input and not args.no_preview:
        sheet = contact_sheet(out_dir)
        print(f"\nContact sheet: {sheet}")

    print(f"\nDone. STLs are in: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
