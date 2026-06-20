"""Build framed-lithophane STL files from images.

A lithophane encodes an image in *material thickness*: dark pixels become
thick (block light), bright pixels become thin (pass light). Backlit, the
picture appears. We build the panel and a raised picture frame as a single
watertight heightmap solid:

    height(x, y) = frame_depth          in the border region (tall = the frame)
                 = thickness(image)     in the inner region  (the lithophane)

The back is flat at z = 0, so it sits on the print bed and needs no supports.
Light comes through from behind when wall-mounted or set on a lightbox.

No boolean unions are used — the whole part is one heightmap surface, which
keeps the mesh manifold without needing an OpenSCAD/Blender/manifold backend.
"""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.ndimage import gaussian_filter
import trimesh


# Built-in procedural scenes so the factory produces sellable output with no
# input photos. Each maps to a render function in sample_image().
SAMPLE_SCENES = ("mountains", "moon-phases", "portrait-bokeh", "wave")

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


@dataclass
class LithophaneSpec:
    """One framed lithophane's printable parameters (all millimetres)."""

    name: str
    image_width_mm: float = 100.0    # width of the *image* area (frame adds more)
    pixel_pitch_mm: float = 0.3      # XY size of one image pixel on the panel
    min_thickness_mm: float = 0.8    # thinnest material (brightest pixels)
    max_thickness_mm: float = 3.0    # thickest material (darkest pixels)
    frame_width_mm: float = 8.0      # border width around the image
    frame_depth_mm: float = 4.5      # how tall the frame stands off the back
    gamma: float = 1.6               # >1 boosts midtone contrast when backlit
    invert: bool = False             # set True for negatives / X-ray look
    smooth_sigma: float = 0.6        # gentle blur to tame single-pixel spikes

    def __post_init__(self) -> None:
        if self.max_thickness_mm <= self.min_thickness_mm:
            raise ValueError("max_thickness_mm must exceed min_thickness_mm")
        if self.frame_depth_mm < self.max_thickness_mm:
            # The frame must out-stand the thickest part of the image, or it
            # would not read as a raised border.
            self.frame_depth_mm = self.max_thickness_mm + 1.0


def image_to_thickness(img: Image.Image, spec: LithophaneSpec) -> np.ndarray:
    """Map a PIL image to a per-pixel thickness array (mm), image region only."""
    target_w = max(8, int(round(spec.image_width_mm / spec.pixel_pitch_mm)))
    gray = ImageOps.grayscale(img)
    # Auto-stretch contrast so faint photos still use the full thickness range.
    gray = ImageOps.autocontrast(gray, cutoff=1)
    w, h = gray.size
    target_h = max(8, int(round(target_w * h / w)))
    gray = gray.resize((target_w, target_h), Image.LANCZOS)

    bright = np.asarray(gray, dtype=np.float32) / 255.0
    if spec.invert:
        bright = 1.0 - bright
    # Gamma on brightness sharpens midtone separation once backlit.
    bright = np.clip(bright, 0.0, 1.0) ** (1.0 / spec.gamma)

    # Bright -> thin, dark -> thick.
    thickness = spec.max_thickness_mm - bright * (
        spec.max_thickness_mm - spec.min_thickness_mm
    )
    if spec.smooth_sigma > 0:
        thickness = gaussian_filter(thickness, sigma=spec.smooth_sigma)
    return thickness.astype(np.float32)


def _frame_heightmap(thickness: np.ndarray, spec: LithophaneSpec):
    """Embed the image-thickness array inside a raised frame border.

    Returns (heights, pitch) where heights is the full top-surface heightmap
    (frame + image) and pitch is the XY size of one cell in mm.
    """
    pitch = spec.pixel_pitch_mm
    border = max(1, int(round(spec.frame_width_mm / pitch)))
    h, w = thickness.shape
    H, W = h + 2 * border, w + 2 * border

    heights = np.full((H, W), spec.frame_depth_mm, dtype=np.float32)
    heights[border:border + h, border:border + w] = thickness
    return heights, pitch


def heightmap_to_solid(heights: np.ndarray, pitch: float) -> trimesh.Trimesh:
    """Convert a top-surface heightmap into a watertight flat-backed solid.

    Vertices are placed at grid corners; the top follows `heights`, the bottom
    is flat at z=0, and the four borders are stitched with vertical walls.
    """
    H, W = heights.shape
    xs = (np.arange(W) * pitch).astype(np.float32)
    ys = (np.arange(H) * pitch).astype(np.float32)
    gx, gy = np.meshgrid(xs, ys)

    n = H * W
    top = np.column_stack([gx.ravel(), gy.ravel(), heights.ravel()])
    bottom = np.column_stack([gx.ravel(), gy.ravel(), np.zeros(n, np.float32)])
    verts = np.vstack([top, bottom]).astype(np.float32)

    # Cell corner indices for the top grid (bottom = same + n).
    rr, cc = np.meshgrid(np.arange(H - 1), np.arange(W - 1), indexing="ij")
    v00 = (rr * W + cc).ravel()
    v01 = v00 + 1
    v10 = v00 + W
    v11 = v00 + W + 1

    top_faces = np.vstack([
        np.column_stack([v00, v10, v11]),
        np.column_stack([v00, v11, v01]),
    ])
    bottom_faces = np.vstack([
        np.column_stack([v00 + n, v11 + n, v10 + n]),
        np.column_stack([v00 + n, v01 + n, v11 + n]),
    ])

    # Perimeter loop of top-grid vertex ids, going around the outside once.
    top_edge = [c for c in range(W)]                      # row 0, L->R
    right_edge = [r * W + (W - 1) for r in range(1, H)]   # col W-1, T->B
    bottom_edge = [(H - 1) * W + c for c in range(W - 2, -1, -1)]  # R->L
    left_edge = [r * W for r in range(H - 2, 0, -1)]      # col 0, B->T
    loop = np.array(top_edge + right_edge + bottom_edge + left_edge)

    a = loop
    b = np.roll(loop, -1)
    wall_faces = np.vstack([
        np.column_stack([a, b, b + n]),
        np.column_stack([a, b + n, a + n]),
    ])

    faces = np.vstack([top_faces, bottom_faces, wall_faces])
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    mesh.fix_normals()
    return mesh


# --------------------------------------------------------------------------- #
# Procedural sample scenes (so the factory works with zero input photos).
# --------------------------------------------------------------------------- #

def _normalize(a: np.ndarray) -> np.ndarray:
    a = a - a.min()
    m = a.max()
    return a / m if m > 0 else a


def sample_image(scene: str, size: int = 600) -> Image.Image:
    """Render a built-in grayscale demo scene as a PIL image."""
    if scene not in SAMPLE_SCENES:
        raise ValueError(f"unknown scene {scene!r}; pick from {SAMPLE_SCENES}")
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    nx, ny = x / size, y / size

    if scene == "mountains":
        sky = np.clip(0.95 - ny * 0.6, 0, 1)
        ridge = np.zeros(size, np.float32)
        rng = np.random.default_rng(7)
        for amp, freq, base in [(0.18, 3, 0.45), (0.10, 7, 0.30), (0.05, 17, 0.20)]:
            ph = rng.uniform(0, 2 * np.pi)
            ridge += base / 3 + amp * (0.5 + 0.5 * np.sin(freq * nx[0] * 2 * np.pi + ph))
        horizon = 0.45 + ridge
        mountain = (ny > horizon[None, :]).astype(np.float32)
        img = sky * (1 - mountain) + mountain * (0.15 + 0.25 * ny)
        # A soft sun glow upper-right.
        img += 0.5 * np.exp(-(((nx - 0.78) ** 2 + (ny - 0.22) ** 2) / 0.01))

    elif scene == "moon-phases":
        img = np.full((size, size), 0.05, np.float32)
        for i, frac in enumerate(np.linspace(-1, 1, 4)):
            cx = (i + 0.5) / 4
            r = 0.09
            d = np.sqrt((nx - cx) ** 2 + (ny - 0.5) ** 2)
            disc = d < r
            # Terminator: shade by horizontal position within the disc.
            shade = np.clip(0.5 + 0.5 * np.sign(frac) *
                            ((nx - cx) / r - frac), 0, 1)
            img = np.where(disc, 0.2 + 0.8 * shade, img)

    elif scene == "portrait-bokeh":
        # Centered soft oval "subject" over blurred light blobs.
        rng = np.random.default_rng(3)
        img = np.full((size, size), 0.25, np.float32)
        for _ in range(40):
            bx, by = rng.uniform(0, 1, 2)
            br = rng.uniform(0.02, 0.06)
            img += rng.uniform(0.1, 0.4) * np.exp(
                -(((nx - bx) ** 2 + (ny - by) ** 2) / (br ** 2)))
        oval = (((nx - 0.5) / 0.28) ** 2 + ((ny - 0.45) / 0.36) ** 2)
        subject = np.clip(1.0 - oval, 0, 1)
        img = img * (1 - subject) + subject * (0.85 - 0.3 * ny)

    else:  # wave
        img = (0.5 + 0.5 * np.sin(8 * np.pi * nx + 3 * np.sin(4 * np.pi * ny)))
        img *= np.clip(1.1 - ny, 0.2, 1)

    arr = (_normalize(gaussian_filter(img, sigma=1.5)) * 255).astype(np.uint8)
    pil = Image.fromarray(arr, "L")
    # A small caption is fun on demos but would print as a thick bar; skip it.
    return pil


def build_one(spec: LithophaneSpec, out_dir: Path,
              img: Image.Image | None = None,
              target_face_count: int | None = None) -> Path:
    """Generate the STL (and return its path) for one framed lithophane.

    If `img` is None, `spec.name` must be one of SAMPLE_SCENES.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    if img is None:
        img = sample_image(spec.name)

    thickness = image_to_thickness(img, spec)
    heights, pitch = _frame_heightmap(thickness, spec)
    mesh = heightmap_to_solid(heights, pitch)

    if target_face_count and mesh.faces.shape[0] > target_face_count:
        mesh = mesh.simplify_quadric_decimation(face_count=target_face_count)

    mesh.apply_translation(-mesh.bounds[0])  # origin at min corner
    stl_path = out_dir / f"lithophane_{spec.name}.stl"
    mesh.export(str(stl_path))
    return stl_path
