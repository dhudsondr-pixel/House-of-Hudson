"""Generate 26 puffy bubble letter STL files for 3D printing on a Bambu.

Approach: render each letter from a bold TrueType font as a 2D mask, smooth
the silhouette to round corners, compute distance-to-edge for each interior
pixel, use that as a dome heightmap, then marching-cubes a 3D voxel volume
into a triangle mesh.

Output is flat-bottom + puffy-top — sits flat on the print bed (no supports
needed) and shows the bubble dome to the viewer when wall-mounted.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, gaussian_filter, binary_dilation
from skimage.measure import marching_cubes
import trimesh


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TARGET_LETTER_HEIGHT_MM = 60.0
TARGET_PUFF_HEIGHT_MM = 18.0
VOXEL_SIZE_MM = 0.4
PAD_VOXELS = 4
SILHOUETTE_SMOOTH_SIGMA = 2.2
# Fatten strokes by ~7% of the letter cap height — DejaVu Bold by itself is
# too lean to read as "bubble". Dilation widens evenly without changing height.
STROKE_FATTEN_FRACTION = 0.07
# Marching cubes overshoots — 100k+ faces per letter is far more resolution
# than a 60mm print needs. Decimate to a budget that still looks smooth.
TARGET_FACE_COUNT = 12000


def render_letter_mask(letter: str, target_height_px: int) -> np.ndarray:
    fnt = ImageFont.truetype(FONT_PATH, target_height_px * 2)
    bbox = fnt.getbbox(letter)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = max(4, target_height_px // 5)
    img = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    ImageDraw.Draw(img).text(
        (pad - bbox[0], pad - bbox[1]), letter, font=fnt, fill=255
    )
    arr = np.array(img)
    ys, xs = np.where(arr > 127)
    y0, y1 = ys.min(), ys.max() + 1
    x0, x1 = xs.min(), xs.max() + 1
    cropped = arr[y0:y1, x0:x1]
    # Resize so cap height matches target exactly across all letters.
    scale = target_height_px / (y1 - y0)
    new_w = max(1, int(round((x1 - x0) * scale)))
    img_resized = Image.fromarray(cropped).resize(
        (new_w, target_height_px), Image.LANCZOS
    )
    mask_f = np.array(img_resized).astype(np.float32) / 255.0
    mask = mask_f > 0.5
    # Fatten the strokes so the silhouette reads as bubble-letter chunky.
    dilate_iters = max(1, int(round(STROKE_FATTEN_FRACTION * target_height_px)))
    mask = binary_dilation(mask, iterations=dilate_iters)
    # Round sharp corners by blurring the (now-fatter) mask and re-threshold.
    smoothed = gaussian_filter(mask.astype(np.float32), sigma=SILHOUETTE_SMOOTH_SIGMA)
    return smoothed > 0.5


def puff_mesh(mask: np.ndarray, puff_h_voxels: float) -> trimesh.Trimesh | None:
    dist = distance_transform_edt(mask)
    max_d = dist.max()
    if max_d < 1:
        return None
    # sin(pi/2 · d/max) gives a fuller balloon dome — tangent flat at the centre,
    # smooth taper into the silhouette edge instead of a sharp drop-off.
    h_top = puff_h_voxels * np.sin(np.pi / 2 * dist / max_d)

    pad = PAD_VOXELS
    mask_p = np.pad(mask, pad, constant_values=False)
    h_top_p = np.pad(h_top, pad, constant_values=0.0)

    H, W = mask_p.shape
    Z = int(np.ceil(puff_h_voxels)) + 2 * pad + 1
    z_grid = np.arange(Z, dtype=np.float32) - pad

    volume = (
        (z_grid[:, None, None] >= 0)
        & (z_grid[:, None, None] <= h_top_p[None, :, :])
        & mask_p[None, :, :]
    )

    verts, faces, _, _ = marching_cubes(volume.astype(np.float32), level=0.5)
    # marching_cubes returns (z, y, x); convert to (x, y, z).
    verts = verts[:, [2, 1, 0]]
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    mesh.fix_normals()
    return mesh


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent / "output-bubble-letters"
    out_dir.mkdir(exist_ok=True)

    target_h_px = int(round(TARGET_LETTER_HEIGHT_MM / VOXEL_SIZE_MM))
    puff_h_voxels = TARGET_PUFF_HEIGHT_MM / VOXEL_SIZE_MM

    print(
        f"Generating {len(LETTERS)} letters · "
        f"{TARGET_LETTER_HEIGHT_MM}mm cap × "
        f"{TARGET_PUFF_HEIGHT_MM}mm thick · {VOXEL_SIZE_MM}mm voxels\n"
    )
    for letter in LETTERS:
        mask = render_letter_mask(letter, target_h_px)
        mesh = puff_mesh(mask, puff_h_voxels)
        if mesh is None:
            print(f"  - {letter}: empty mask, skipped")
            continue
        if mesh.faces.shape[0] > TARGET_FACE_COUNT:
            mesh = mesh.simplify_quadric_decimation(face_count=TARGET_FACE_COUNT)
        mesh.apply_scale(VOXEL_SIZE_MM)
        mesh.apply_translation(-mesh.bounds[0])  # origin at min corner
        out_path = out_dir / f"letter_{letter}.stl"
        mesh.export(str(out_path))
        kb = out_path.stat().st_size // 1024
        bb = mesh.bounds[1] - mesh.bounds[0]
        print(
            f"  {letter}  {bb[0]:5.1f} × {bb[1]:5.1f} × {bb[2]:4.1f} mm  "
            f"{mesh.faces.shape[0]:>6} faces  {kb:>4} KB"
        )
    print(f"\nWrote STLs to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
