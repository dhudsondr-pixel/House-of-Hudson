"""Core orientation + settings analysis for 3D print models.

The orientation algorithm is a simplified Tweaker-3:
for each candidate "down" direction, rotate the mesh and score it on
(bed contact area, overhang area, Z-height). Candidates are drawn from
the axis directions plus the dominant face normals of the mesh.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np
import trimesh


BOTTOM_NORMAL_TOLERANCE = 0.99
OVERHANG_THRESHOLD = 0.5
TOP_FACE_CANDIDATES = 12


@dataclass
class OrientationScore:
    rotation_matrix: list[list[float]]
    down_direction: list[float]
    bed_contact_area_mm2: float
    overhang_area_mm2: float
    height_mm: float
    footprint_mm2: float
    score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PrintSettings:
    layer_height_mm: float
    wall_count: int
    top_bottom_layers: int
    infill_percent: int
    infill_pattern: str
    print_speed_mm_s: int
    outer_wall_speed_mm_s: int
    supports_required: bool
    support_overhang_angle_deg: int
    brim_recommended: bool
    rationale: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _rotation_between(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    source = source / np.linalg.norm(source)
    target = target / np.linalg.norm(target)
    cross = np.cross(source, target)
    dot = float(np.dot(source, target))
    if np.isclose(dot, 1.0):
        return np.eye(4)
    if np.isclose(dot, -1.0):
        axis = np.array([1.0, 0.0, 0.0])
        if abs(source[0]) > 0.9:
            axis = np.array([0.0, 1.0, 0.0])
        return trimesh.transformations.rotation_matrix(np.pi, axis)
    axis = cross / np.linalg.norm(cross)
    angle = np.arccos(np.clip(dot, -1.0, 1.0))
    return trimesh.transformations.rotation_matrix(angle, axis)


def _candidate_directions(mesh: trimesh.Trimesh) -> np.ndarray:
    axes = np.array(
        [
            [0, 0, -1], [0, 0, 1],
            [0, -1, 0], [0, 1, 0],
            [-1, 0, 0], [1, 0, 0],
        ],
        dtype=float,
    )
    normals = mesh.face_normals
    areas = mesh.area_faces
    order = np.argsort(areas)[::-1][:TOP_FACE_CANDIDATES]
    dominant = -normals[order]
    candidates = np.vstack([axes, dominant])
    unique = []
    for c in candidates:
        c = c / np.linalg.norm(c)
        if not any(np.dot(c, u) > 0.995 for u in unique):
            unique.append(c)
    return np.array(unique)


def _score_orientation(mesh: trimesh.Trimesh, down: np.ndarray) -> OrientationScore:
    rotation = _rotation_between(down, np.array([0.0, 0.0, -1.0]))
    rotated = mesh.copy()
    rotated.apply_transform(rotation)
    rotated.apply_translation([0, 0, -rotated.bounds[0, 2]])

    normals = rotated.face_normals
    areas = rotated.area_faces

    bottom_mask = normals[:, 2] < -BOTTOM_NORMAL_TOLERANCE
    bed_area = float(areas[bottom_mask].sum())

    overhang_mask = (normals[:, 2] < -OVERHANG_THRESHOLD) & ~bottom_mask
    overhang_weights = -normals[overhang_mask, 2] - OVERHANG_THRESHOLD
    overhang_area = float((areas[overhang_mask] * overhang_weights).sum())

    extents = rotated.bounds[1] - rotated.bounds[0]
    height = float(extents[2])
    footprint = float(extents[0] * extents[1])

    bed_term = bed_area / max(footprint, 1.0)
    overhang_term = overhang_area / max(mesh.area, 1.0)
    height_term = height / max(float(mesh.extents.max()), 1.0)

    score = 1.5 * bed_term - 2.0 * overhang_term - 0.7 * height_term

    return OrientationScore(
        rotation_matrix=rotation.tolist(),
        down_direction=down.tolist(),
        bed_contact_area_mm2=bed_area,
        overhang_area_mm2=overhang_area,
        height_mm=height,
        footprint_mm2=footprint,
        score=score,
    )


def rank_orientations(mesh: trimesh.Trimesh, top_n: int = 5) -> list[OrientationScore]:
    candidates = _candidate_directions(mesh)
    scored = [_score_orientation(mesh, d) for d in candidates]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored[:top_n]


def apply_orientation(mesh: trimesh.Trimesh, orientation: OrientationScore) -> trimesh.Trimesh:
    oriented = mesh.copy()
    oriented.apply_transform(np.array(orientation.rotation_matrix))
    oriented.apply_translation([0, 0, -oriented.bounds[0, 2]])
    return oriented


def recommend_settings(
    oriented_mesh: trimesh.Trimesh, orientation: OrientationScore
) -> PrintSettings:
    extents = oriented_mesh.extents
    max_dim = float(extents.max())
    min_dim = float(extents.min())
    volume_cm3 = float(oriented_mesh.volume) / 1000.0
    rationale: list[str] = []

    if max_dim < 25:
        layer_height = 0.12
        rationale.append("Small part (<25mm): fine layers for detail.")
    elif max_dim < 80:
        layer_height = 0.20
        rationale.append("Medium part: 0.20mm balances detail and speed.")
    elif max_dim < 200:
        layer_height = 0.24
        rationale.append("Large part: 0.24mm to save time without losing much detail.")
    else:
        layer_height = 0.28
        rationale.append("Very large part: 0.28mm for fastest reasonable quality.")

    if volume_cm3 < 5:
        infill = 25
    elif volume_cm3 < 50:
        infill = 18
    elif volume_cm3 < 250:
        infill = 12
    else:
        infill = 10
    rationale.append(f"Infill {infill}% from volume {volume_cm3:.1f} cm^3.")

    walls = 3 if min_dim > 2.0 else 2
    rationale.append(f"{walls} walls (min wall-friendly dimension {min_dim:.1f}mm).")

    top_bottom = max(3, int(round(0.8 / layer_height)))

    print_speed = 80 if max_dim > 60 else 60
    outer_speed = max(25, int(print_speed * 0.45))
    rationale.append(
        f"Print speed {print_speed} mm/s, outer wall {outer_speed} mm/s for surface quality."
    )

    overhang_ratio = float(orientation.overhang_area_mm2) / max(float(oriented_mesh.area), 1.0)
    supports_required = bool(overhang_ratio > 0.02)
    if supports_required:
        rationale.append(
            f"Supports recommended: ~{overhang_ratio * 100:.1f}% of surface is steep overhang."
        )
    else:
        rationale.append("Negligible overhangs in this orientation; supports likely not needed.")

    brim_recommended = bool(orientation.bed_contact_area_mm2 < 400 or max_dim > 150)
    if brim_recommended:
        rationale.append("Brim recommended (small footprint or tall/long part).")

    return PrintSettings(
        layer_height_mm=layer_height,
        wall_count=walls,
        top_bottom_layers=top_bottom,
        infill_percent=infill,
        infill_pattern="gyroid",
        print_speed_mm_s=print_speed,
        outer_wall_speed_mm_s=outer_speed,
        supports_required=supports_required,
        support_overhang_angle_deg=50,
        brim_recommended=brim_recommended,
        rationale=rationale,
    )


def analyze(mesh: trimesh.Trimesh) -> dict[str, Any]:
    if not mesh.is_watertight:
        mesh.fill_holes()
    orientations = rank_orientations(mesh)
    best = orientations[0]
    oriented = apply_orientation(mesh, best)
    settings = recommend_settings(oriented, best)
    return {
        "input": {
            "triangle_count": int(len(mesh.faces)),
            "volume_mm3": float(mesh.volume),
            "surface_area_mm2": float(mesh.area),
            "bounding_box_mm": mesh.extents.tolist(),
            "watertight": bool(mesh.is_watertight),
        },
        "best_orientation": best.to_dict(),
        "alternative_orientations": [o.to_dict() for o in orientations[1:]],
        "recommended_settings": settings.to_dict(),
        "_oriented_mesh": oriented,
    }
