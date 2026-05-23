"""Render a single PNG contact sheet of all 26 bubble letters from above.

Uses a fake-lighting shader on the heightmap (no 3D renderer needed, so this
runs headless on any machine). Output is a phone-friendly preview so the
shop owner can eyeball proportions without opening every STL in a viewer.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, gaussian_filter, sobel

from .generate import (
    LETTERS, FONT_PATH, TARGET_LETTER_HEIGHT_MM, TARGET_PUFF_HEIGHT_MM,
    VOXEL_SIZE_MM, render_letter_mask,
)


CELL_PX = 280
COLS = 6
ROWS = 5  # 30 cells, last 4 are blank — keeps the grid square-ish
BG = (38, 42, 50)             # dark slate so the glossy white pops
LETTER_MID = (220, 215, 208)  # mid-tone base for the puff body
LETTER_LIT = (255, 252, 246)  # lit highlight (light hits dome top)
LETTER_DARK = (95, 90, 85)    # deep shadow on the receded side


def shade_letter(mask: np.ndarray, puff_h_voxels: float) -> Image.Image:
    """Render one letter as a top-down shaded heightmap (fake 3D, glossy)."""
    dist = distance_transform_edt(mask)
    max_d = max(dist.max(), 1)
    h_top = puff_h_voxels * np.sin(np.pi / 2 * dist / max_d)

    # Surface gradients → diffuse + specular shading (light from upper-left).
    h_smooth = gaussian_filter(h_top, sigma=1.4)
    gy = sobel(h_smooth, axis=0)
    gx = sobel(h_smooth, axis=1)
    # Normal vector (unnormalized): (-gx, -gy, 1)
    nz = np.ones_like(gx)
    norm = np.sqrt(gx * gx + gy * gy + nz * nz)
    nx, ny, nz = -gx / norm, -gy / norm, nz / norm

    light = np.array([-0.6, -0.6, 0.6])
    light /= np.linalg.norm(light)
    diffuse = np.clip(nx * light[0] + ny * light[1] + nz * light[2], 0, 1)
    # Specular: tight highlight where the surface faces the light directly.
    spec = np.clip(diffuse, 0, 1) ** 18

    rgb = np.zeros((*mask.shape, 3), dtype=np.float32)
    for c in range(3):
        rgb[..., c] = (
            LETTER_DARK[c] * (1 - diffuse)
            + LETTER_MID[c] * diffuse
            + (LETTER_LIT[c] - LETTER_MID[c]) * spec
        )
    # Soft drop shadow just outside the silhouette so the letter "sits" on bg.
    out_dist = distance_transform_edt(~mask)
    shadow = np.clip(1.0 - out_dist / 12.0, 0, 1) * 0.55
    for c, bg in enumerate(BG):
        bg_shaded = bg * (1 - shadow)
        rgb[..., c] = np.where(mask, rgb[..., c], bg_shaded)
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))


def fit_into_cell(img: Image.Image, cell_px: int, margin: int = 24) -> Image.Image:
    """Center the letter image in a square cell, preserving aspect ratio."""
    target = cell_px - 2 * margin
    w, h = img.size
    scale = target / max(w, h)
    new_w, new_h = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    cell = Image.new("RGB", (cell_px, cell_px), BG)
    cell.paste(resized, ((cell_px - new_w) // 2, (cell_px - new_h) // 2))
    return cell


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent / "output-bubble-letters"
    out_dir.mkdir(exist_ok=True)

    target_h_px = int(round(TARGET_LETTER_HEIGHT_MM / VOXEL_SIZE_MM))
    puff_h_voxels = TARGET_PUFF_HEIGHT_MM / VOXEL_SIZE_MM

    sheet = Image.new("RGB", (COLS * CELL_PX, ROWS * CELL_PX), BG)
    d = ImageDraw.Draw(sheet)
    try:
        label_font = ImageFont.truetype(FONT_PATH, 22)
    except Exception:
        label_font = ImageFont.load_default()

    for i, letter in enumerate(LETTERS):
        mask = render_letter_mask(letter, target_h_px)
        shaded = shade_letter(mask, puff_h_voxels)
        cell = fit_into_cell(shaded, CELL_PX)
        col, row = i % COLS, i // COLS
        sheet.paste(cell, (col * CELL_PX, row * CELL_PX))
        d.text((col * CELL_PX + 12, row * CELL_PX + 8),
               letter, font=label_font, fill=(150, 150, 160))

    sheet_path = out_dir / "_preview_contact_sheet.png"
    sheet.save(sheet_path, "PNG", optimize=True)
    print(f"Wrote {sheet_path}  ({sheet_path.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
