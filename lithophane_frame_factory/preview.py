"""Backlit previews so the shop owner sees the result without printing.

A lithophane's apparent brightness follows Beer-Lambert: transmitted light
falls off exponentially with thickness, I = I0 * exp(-mu * thickness). The
thick frame goes dark, the thin (bright) image areas glow. We render that with
a warm LED tint to mimic a real lightbox photo.
"""

from pathlib import Path

import numpy as np
from PIL import Image

from .generate import (
    LithophaneSpec, SAMPLE_SCENES, sample_image, image_to_thickness,
    _frame_heightmap,
)


# Light absorption coefficient (1/mm) for a typical white PLA wall. Tuned so
# min/max thickness span a pleasing bright-to-dark range when lit.
MU = 1.05
LED_TINT = np.array([1.0, 0.96, 0.88])  # warm white
BG = (24, 24, 28)


def backlit_image(spec: LithophaneSpec, img: Image.Image | None = None,
                  scale_px: int = 520) -> Image.Image:
    """Render one framed lithophane as it would look backlit on a lightbox."""
    if img is None:
        img = sample_image(spec.name)
    thickness = image_to_thickness(img, spec)
    heights, _ = _frame_heightmap(thickness, spec)

    transmit = np.exp(-MU * heights)            # 0 (opaque) .. ~1 (clear)
    transmit = transmit / transmit.max()        # normalize brightest -> 1
    rgb = (transmit[..., None] * LED_TINT[None, None, :])
    rgb = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)

    pil = Image.fromarray(rgb, "RGB")
    w, h = pil.size
    scale = scale_px / max(w, h)
    return pil.resize((max(1, int(w * scale)), max(1, int(h * scale))),
                      Image.LANCZOS)


def contact_sheet(out_dir: Path) -> Path:
    """Backlit preview of every built-in sample scene, in one PNG."""
    cells = []
    for scene in SAMPLE_SCENES:
        spec = LithophaneSpec(name=scene)
        cells.append((scene, backlit_image(spec)))

    cols = 2
    rows = (len(cells) + cols - 1) // cols
    cw = max(c.size[0] for _, c in cells)
    ch = max(c.size[1] for _, c in cells)
    pad = 18
    sheet = Image.new(
        "RGB",
        (cols * cw + (cols + 1) * pad, rows * ch + (rows + 1) * pad),
        BG,
    )
    for i, (_, cell) in enumerate(cells):
        col, row = i % cols, i // cols
        x = pad + col * (cw + pad) + (cw - cell.size[0]) // 2
        y = pad + row * (ch + pad) + (ch - cell.size[1]) // 2
        sheet.paste(cell, (x, y))

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "_preview_backlit_sheet.png"
    sheet.save(path, "PNG", optimize=True)
    return path
