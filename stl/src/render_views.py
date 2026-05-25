"""Headless STL preview rendering using matplotlib.

Produces clean isometric / top / front PNGs suitable for marketing listings.
No GPU, no Blender, no system libs beyond matplotlib's own deps.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.colors import LightSource
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# Background and material colors per "style".
STYLES = {
    "studio_white": {"bg": "#f5f5f5", "facecolor": "#a8b3c4", "edge": "#1a1a1a"},
    "midnight":     {"bg": "#0e1320", "facecolor": "#d4af37", "edge": "#0a0a14"},
    "blueprint":    {"bg": "#0d3050", "facecolor": "#e8f1fb", "edge": "#082238"},
    "industrial":   {"bg": "#1a1a1a", "facecolor": "#f57b00", "edge": "#0e0e0e"},
    "soft_pastel":  {"bg": "#f0ebe2", "facecolor": "#cda782", "edge": "#5e4a32"},
    "neon":         {"bg": "#101018", "facecolor": "#7df9ff", "edge": "#020208"},
}

# Camera angles for each named view.
VIEWS = {
    "iso":   {"elev": 28, "azim": -55},
    "front": {"elev": 6,  "azim": -90},
    "top":   {"elev": 88, "azim": -90},
    "back":  {"elev": 12, "azim": 90},
    "left":  {"elev": 10, "azim": 0},
}


def _load_concat(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load_mesh(str(path))
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(
            [g for g in mesh.geometry.values() if hasattr(g, "vertices")]
        )
    return mesh


def _decimate_if_huge(mesh: trimesh.Trimesh, max_faces: int = 60000) -> trimesh.Trimesh:
    """Matplotlib's poly collection becomes slow past ~60k triangles."""
    if len(mesh.faces) <= max_faces:
        return mesh
    target = max_faces / len(mesh.faces)
    try:
        return mesh.simplify_quadric_decimation(int(len(mesh.faces) * target))
    except Exception:
        # Fallback: keep every Nth face (visual approximation).
        step = max(1, int(len(mesh.faces) / max_faces))
        keep = np.arange(0, len(mesh.faces), step)
        return mesh.submesh([keep], append=True)


def render_view(
    stl_path: Path,
    out_path: Path,
    view: str = "iso",
    size_px: int = 1200,
    style: str = "studio_white",
) -> Path:
    """Render a single view of an STL to a PNG."""
    mesh = _load_concat(stl_path)
    mesh = _decimate_if_huge(mesh)

    s = STYLES.get(style, STYLES["studio_white"])
    v = VIEWS.get(view, VIEWS["iso"])

    # Build Poly3DCollection from triangle faces.
    tris = mesh.triangles  # (n, 3, 3)

    # Center & scale for a clean framing.
    centroid = mesh.centroid
    centered = tris - centroid

    fig = plt.figure(figsize=(size_px / 150, size_px / 150), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor(s["bg"])
    ax.set_facecolor(s["bg"])

    # Shade per face via simple lambertian using face normals.
    normals = mesh.face_normals  # (n, 3)
    # Light from upper-front-right.
    light_dir = np.array([0.4, -0.5, 1.0])
    light_dir = light_dir / np.linalg.norm(light_dir)
    shade = np.clip(normals @ light_dir, 0.05, 1.0)

    # Convert base color to RGB and modulate by shade.
    base = np.array(matplotlib.colors.to_rgb(s["facecolor"]))
    face_colors = np.clip(base[None, :] * (0.35 + 0.65 * shade[:, None]), 0, 1)
    face_colors_rgba = np.concatenate([face_colors, np.ones((len(face_colors), 1))], axis=1)

    coll = Poly3DCollection(
        centered,
        facecolors=face_colors_rgba,
        edgecolors=s["edge"],
        linewidths=0.05,
    )
    ax.add_collection3d(coll)

    # Equal axis ranges so the model isn't squished.
    extents = mesh.bounding_box.extents
    max_extent = max(extents) * 0.55
    ax.set_xlim(-max_extent, max_extent)
    ax.set_ylim(-max_extent, max_extent)
    ax.set_zlim(-max_extent, max_extent)
    ax.set_box_aspect((1, 1, 1))

    # Clean look: hide axes, panes, grid.
    ax.set_axis_off()
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.pane.fill = False
        pane.pane.set_edgecolor((0, 0, 0, 0))

    ax.view_init(elev=v["elev"], azim=v["azim"])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        out_path,
        facecolor=s["bg"],
        bbox_inches="tight",
        pad_inches=0.1,
        dpi=150,
    )
    plt.close(fig)
    return out_path


def render_all_views(
    stl_path: Path,
    out_dir: Path,
    style: str = "studio_white",
    views: list[str] | None = None,
) -> list[Path]:
    views = views or ["iso", "front", "top"]
    paths: list[Path] = []
    for v in views:
        p = render_view(stl_path, out_dir / f"render_{v}.png", view=v, style=style)
        paths.append(p)
    return paths
