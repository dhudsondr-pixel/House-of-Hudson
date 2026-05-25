"""STL analysis: dimensions, volume, weight, print-time estimate, suggested price."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh


# Material density (g/cm^3). User can override per material.
MATERIAL_DENSITY = {
    "PLA":  1.24,
    "PETG": 1.27,
    "ABS":  1.04,
    "TPU":  1.21,
    "ASA":  1.07,
    "Nylon": 1.13,
    "Resin": 1.10,
}


@dataclass
class STLAnalysis:
    path: Path
    bbox_mm: tuple[float, float, float]      # width, depth, height
    volume_cm3: float                         # solid model volume
    surface_area_cm2: float
    is_watertight: bool
    triangle_count: int

    # Filled-print estimates (assume infill).
    filament_weight_g: float                  # weight at the chosen infill
    filament_length_m: float                  # rough estimate at 1.75mm

    # Print time estimate (hours), heuristic.
    print_time_hours: float

    material: str
    infill_pct: int

    def fits_on_bed(self, bed_x_mm: float, bed_y_mm: float, bed_z_mm: float) -> bool:
        w, d, h = sorted(self.bbox_mm, reverse=True)
        bed = sorted([bed_x_mm, bed_y_mm, bed_z_mm], reverse=True)
        return w <= bed[0] and d <= bed[1] and h <= bed[2]


def _estimate_filled_weight_g(
    solid_volume_cm3: float,
    bbox_cm3: float,
    density: float,
    infill_pct: int,
    shell_factor: float = 0.18,
) -> float:
    """Estimate the actual extruded plastic mass for a sliced print.

    A printed solid is mostly air. The model's *solid volume* (what trimesh
    reports) overstates extrusion. We approximate the printed mass as:
        shell_mass + infill_mass
    where:
        shell_mass  ~ shell_factor * solid_volume * density   (perimeters + tops/bottoms)
        infill_mass ~ (1 - shell_factor) * solid_volume * (infill_pct/100) * density
    This roughly matches what slicers report for typical 0.4mm nozzle, 2-3
    perimeter, 4-6 top/bottom layer settings.
    """
    shell = shell_factor * solid_volume_cm3 * density
    interior = (1 - shell_factor) * solid_volume_cm3 * (infill_pct / 100) * density
    return shell + interior


def _estimate_print_time_hours(
    extruded_cm3: float,
    bbox_mm: tuple[float, float, float],
    layer_height_mm: float = 0.2,
) -> float:
    """Estimate print time from *extruded plastic volume*, not solid model volume.

    Typical FDM extrusion rate at 0.2mm layers, 60 mm/s outer wall:
        - small/detailed prints  (<5 cm^3 extruded):   ~3 cm^3 per hour
        - typical prints         (5-30 cm^3):           ~5 cm^3 per hour
        - bulky/infill-heavy     (>30 cm^3):            ~7 cm^3 per hour

    Add a per-layer floor (~5 sec per layer) for tall thin prints whose time
    is dominated by layer changes rather than extrusion.
    """
    if extruded_cm3 < 5:
        rate = 3.0
    elif extruded_cm3 < 30:
        rate = 5.0
    else:
        rate = 7.0

    extrusion_hours = extruded_cm3 / rate

    # Per-layer floor.
    z_mm = max(bbox_mm)
    layer_count = z_mm / max(0.05, layer_height_mm)
    layer_floor_hours = (layer_count * 5) / 3600  # 5 sec per layer

    return max(layer_floor_hours, extrusion_hours)


def analyze_stl(
    path: Path,
    material: str = "PLA",
    infill_pct: int = 20,
) -> STLAnalysis:
    mesh = trimesh.load_mesh(str(path))
    if isinstance(mesh, trimesh.Scene):
        # Sum all geometries if it's a scene (some STLs come in scene wrappers).
        geom = trimesh.util.concatenate([g for g in mesh.geometry.values() if hasattr(g, "vertices")])
        mesh = geom

    bbox = mesh.bounding_box.extents  # (x, y, z) in mm assuming STL is in mm
    bbox_t = (float(bbox[0]), float(bbox[1]), float(bbox[2]))

    # Volume: trimesh reports in cube units = mm^3 if STL is in mm.
    vol_mm3 = float(abs(mesh.volume))
    vol_cm3 = vol_mm3 / 1000.0
    bbox_cm3 = (bbox_t[0] * bbox_t[1] * bbox_t[2]) / 1000.0
    surface_cm2 = float(mesh.area) / 100.0

    density = MATERIAL_DENSITY.get(material, MATERIAL_DENSITY["PLA"])
    weight_g = _estimate_filled_weight_g(vol_cm3, bbox_cm3, density, infill_pct)

    # Filament length (m) from weight, 1.75mm filament: cross-section ~2.405 mm^2 = 0.02405 cm^2.
    # length_cm = volume_cm3 / cross_section_cm2; volume = mass / density.
    filament_vol_cm3 = weight_g / density
    filament_length_cm = filament_vol_cm3 / 0.02405
    filament_length_m = filament_length_cm / 100.0

    # Extruded plastic volume (cm^3) drives realistic print time.
    extruded_cm3 = weight_g / density

    return STLAnalysis(
        path=path,
        bbox_mm=bbox_t,
        volume_cm3=vol_cm3,
        surface_area_cm2=surface_cm2,
        is_watertight=bool(mesh.is_watertight),
        triangle_count=int(len(mesh.faces)),
        filament_weight_g=weight_g,
        filament_length_m=filament_length_m,
        print_time_hours=_estimate_print_time_hours(extruded_cm3, bbox_t),
        material=material,
        infill_pct=infill_pct,
    )


def format_summary(a: STLAnalysis) -> str:
    """Human-readable analysis summary."""
    w, d, h = a.bbox_mm
    lines = [
        f"File:              {a.path.name}",
        f"Bounding box:      {w:.1f} x {d:.1f} x {h:.1f} mm",
        f"Solid volume:      {a.volume_cm3:.1f} cm³  (mesh, before infill)",
        f"Surface area:      {a.surface_area_cm2:.1f} cm²",
        f"Triangles:         {a.triangle_count:,}",
        f"Watertight:        {'yes' if a.is_watertight else 'NO — may need repair before slicing'}",
        f"",
        f"Material:          {a.material} ({MATERIAL_DENSITY.get(a.material, 1.24):.2f} g/cm³)",
        f"Infill:            {a.infill_pct}%",
        f"Est. weight:       {a.filament_weight_g:.1f} g",
        f"Est. filament:     {a.filament_length_m:.1f} m of 1.75mm",
        f"Est. print time:   {a.print_time_hours:.1f} hours  ({int(a.print_time_hours * 60)} min)",
    ]
    return "\n".join(lines)
