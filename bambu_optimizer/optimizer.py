"""Settings recommendation engine.

Given a printer, material, nozzle size, and a print intent (quality target,
part purpose, geometry hints), produce a complete set of slicer values plus a
human-readable rationale.
"""

from dataclasses import dataclass, field, asdict
from typing import Literal

from .materials import MaterialProfile, get_material
from .printers import PrinterProfile, get_printer


QualityTarget = Literal["draft", "standard", "fine", "ultrafine"]
Purpose = Literal["visual", "functional", "mechanical", "miniature", "prototype"]


@dataclass
class PrintIntent:
    quality: QualityTarget = "standard"
    purpose: Purpose = "functional"
    has_overhangs: bool = False
    has_bridges: bool = False
    tall_and_narrow: bool = False        # >3:1 height-to-base
    fine_detail: bool = False            # text, embossing, miniature features
    watertight: bool = False
    transparent: bool = False
    annealed_after: bool = False
    outdoor_use: bool = False
    estimated_part_height_mm: float = 50.0


# Layer-height fractions of nozzle diameter for each quality tier.
LAYER_HEIGHT_RATIOS: dict[QualityTarget, float] = {
    "draft": 0.75,
    "standard": 0.50,
    "fine": 0.35,
    "ultrafine": 0.25,
}

# Speed multipliers applied to the material's base outer-wall speed.
QUALITY_SPEED_MULT: dict[QualityTarget, float] = {
    "draft": 1.20,
    "standard": 1.00,
    "fine": 0.75,
    "ultrafine": 0.55,
}

PURPOSE_INFILL: dict[Purpose, tuple[int, str]] = {
    "visual":     (10, "gyroid"),
    "prototype":  (10, "gyroid"),
    "functional": (20, "gyroid"),
    "mechanical": (40, "gyroid"),
    "miniature":  (15, "gyroid"),
}

PURPOSE_WALLS: dict[Purpose, int] = {
    "visual": 2,
    "prototype": 2,
    "functional": 3,
    "mechanical": 5,
    "miniature": 2,
}


@dataclass
class Recommendation:
    printer: str
    material: str
    nozzle_mm: float

    layer_height_mm: float
    first_layer_height_mm: float
    line_width_mm: float

    walls: int
    top_layers: int
    bottom_layers: int
    infill_pct: int
    infill_pattern: str

    nozzle_temp_c: int
    first_layer_nozzle_temp_c: int
    bed_temp_c: int
    first_layer_bed_temp_c: int
    chamber_temp_c: int

    outer_wall_speed_mm_s: int
    inner_wall_speed_mm_s: int
    infill_speed_mm_s: int
    travel_speed_mm_s: int
    first_layer_speed_mm_s: int
    max_volumetric_flow_mm3s: float

    fan_pct: int
    first_layer_fan_pct: int
    overhang_fan_pct: int

    retraction_mm: float
    z_hop_mm: float

    supports: bool
    support_type: str
    support_overhang_threshold_deg: int

    brim_type: str
    brim_width_mm: float
    bed_surface: str

    adaptive_layer_height: bool
    ironing: bool
    pressure_advance_calibration: str
    flow_calibration: str

    warnings: list[str] = field(default_factory=list)
    rationale: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _round_to(value: float, step: float) -> float:
    return round(round(value / step) * step, 3)


def recommend(
    printer_name: str,
    material_name: str,
    intent: PrintIntent,
    nozzle_mm: float | None = None,
) -> Recommendation:
    printer = get_printer(printer_name)
    material = get_material(material_name)

    nozzle = nozzle_mm if nozzle_mm is not None else printer.default_nozzle_mm
    if nozzle not in printer.nozzle_sizes_mm:
        raise ValueError(
            f"{printer.model} does not support a {nozzle}mm nozzle. "
            f"Options: {printer.nozzle_sizes_mm}"
        )

    warnings: list[str] = []
    rationale: list[str] = []

    if not printer.verified:
        warnings.append(
            f"{printer.model} profile is unverified — confirm specs against your unit."
        )

    if material.requires_enclosure and not printer.enclosed:
        warnings.append(
            f"{material.name} needs an enclosed chamber; {printer.model} is open. "
            "Expect warping, layer splitting, and weak parts."
        )
    if material.chamber_c > 0 and not printer.chamber_heater:
        warnings.append(
            f"{material.name} prefers a {material.chamber_c}C chamber; "
            f"{printer.model} has no active chamber heater. Pre-warm with the bed."
        )
    if material.abrasive:
        warnings.append(
            f"{material.name} is abrasive — use a hardened-steel nozzle, not the brass default."
        )
    if intent.tall_and_narrow and printer.model == "A1":
        warnings.append(
            "A1 is a bedslinger; tall/narrow geometry will ring at high speed. "
            "Cap acceleration to 4000 mm/s^2 and slow outer walls."
        )

    # Geometry
    ratio = LAYER_HEIGHT_RATIOS[intent.quality]
    layer_height = _round_to(nozzle * ratio, 0.04)
    layer_height = max(0.08, min(layer_height, nozzle * 0.75))
    first_layer = _round_to(max(layer_height, 0.20), 0.04)
    line_width = _round_to(nozzle * 1.125, 0.01)

    rationale.append(
        f"Layer height {layer_height}mm = {int(ratio*100)}% of {nozzle}mm nozzle "
        f"({intent.quality} quality)."
    )

    # Shells and infill
    walls = PURPOSE_WALLS[intent.purpose]
    if intent.watertight:
        walls = max(walls, 4)
        rationale.append("Watertight requested → minimum 4 walls.")
    top = max(4, round(1.2 / layer_height))
    bottom = max(3, round(0.8 / layer_height))
    infill_pct, infill_pattern = PURPOSE_INFILL[intent.purpose]
    if intent.purpose == "mechanical" and material.name in ("PA-CF", "PETG-CF", "PC"):
        infill_pct = 60
        rationale.append("High-strength material + mechanical purpose → 60% infill.")

    # Temperatures
    nozzle_c = int(round((material.nozzle_c[0] + material.nozzle_c[1]) / 2))
    # Cooler for fine detail (less stringing/sagging), hotter for high flow
    if intent.fine_detail:
        nozzle_c = max(material.nozzle_c[0], nozzle_c - 5)
        rationale.append("Fine detail → drop nozzle 5C to sharpen features.")
    if nozzle >= 0.6 and intent.quality == "draft":
        nozzle_c = min(material.nozzle_c[1], nozzle_c + 5)
        rationale.append("Large nozzle + draft → +5C to keep flow stable.")
    nozzle_c = min(nozzle_c, printer.max_hotend_c)

    bed_c = int(round((material.bed_c[0] + material.bed_c[1]) / 2))
    bed_c = min(bed_c, printer.max_bed_c)
    first_layer_bed = min(bed_c + 5, printer.max_bed_c)
    first_layer_nozzle = nozzle_c + 5
    first_layer_nozzle = min(first_layer_nozzle, printer.max_hotend_c)

    chamber_c = material.chamber_c if printer.chamber_heater else 0

    # Speeds
    base = material.base_speed_mm_s
    qmult = QUALITY_SPEED_MULT[intent.quality]
    outer = int(base * qmult)
    # Cap outer wall by volumetric flow at this layer height + line width
    flow_cap = (printer.max_volumetric_flow_mm3s /
                (layer_height * line_width))
    if outer > flow_cap:
        outer = int(flow_cap * 0.85)  # 15% headroom
        rationale.append(
            f"Outer wall capped to {outer} mm/s by {printer.model}'s "
            f"{printer.max_volumetric_flow_mm3s} mm^3/s flow ceiling."
        )
    if intent.tall_and_narrow:
        outer = int(outer * 0.7)
        rationale.append("Tall/narrow part → outer wall slowed 30% to reduce ringing.")

    inner = int(outer * 1.4)
    infill_speed = int(outer * 2.0)
    travel = min(printer.max_travel_speed_mm_s, int(outer * 3.0))
    first_layer_speed = max(20, int(outer * 0.3))

    # Volumetric flow target — pick the lower of material and printer
    flow = min(material.base_volumetric_flow_mm3s,
               printer.max_volumetric_flow_mm3s)
    if intent.quality == "draft":
        flow = min(flow * 1.1, printer.max_volumetric_flow_mm3s)
    if intent.quality in ("fine", "ultrafine"):
        flow *= 0.85

    # Cooling
    fan = material.fan_pct
    if intent.has_overhangs or intent.has_bridges:
        fan = min(100, fan + 30) if material.name != "ABS" else 30
        rationale.append("Overhangs/bridges → bump part cooling.")
    if material.name in ("ABS", "ASA", "PC", "PA", "PA-CF") and (intent.has_overhangs or intent.has_bridges):
        warnings.append(
            f"{material.name} dislikes cooling, but you've asked for overhangs. "
            "Expect a quality tradeoff; consider supports or reorientation."
        )
    overhang_fan = 100 if material.name in ("PLA", "PLA+", "PETG", "PETG-CF") else max(fan, 50)

    # Retraction / Z-hop
    retraction = material.retraction_mm
    z_hop = 0.2 if material.name == "TPU" else 0.4

    # Supports
    supports = intent.has_overhangs
    support_type = "tree(auto)" if intent.purpose in ("visual", "miniature") else "normal(auto)"
    if printer.dual_extruder and supports:
        support_type = "normal(auto) with PVA/HIPS interface (dual extruder)"
        rationale.append(
            "Dual-extruder printer → use a dissolvable/break-away interface for clean overhangs."
        )
    support_threshold = 50 if intent.purpose == "miniature" else 55

    # Build plate
    brim_type = "outer_only" if (material.warps or intent.tall_and_narrow) else "no_brim"
    brim_width = 5.0 if material.warps else (3.0 if intent.tall_and_narrow else 0.0)

    # Misc
    adaptive_layer = intent.purpose in ("visual", "miniature") and intent.quality != "draft"
    ironing = intent.purpose == "visual" and intent.quality in ("fine", "ultrafine") and material.name in ("PLA", "PLA+")

    pa_cal = "Run Bambu's auto pressure-advance per filament; re-run if you change brand or color."
    flow_cal = "Run flow-rate calibration tower; ±5% adjustments are normal between spools."

    if material.name == "TPU" and printer.ams_supported and printer.model in ("A1", "P2S", "X2D", "H2C"):
        warnings.append(
            "Soft TPU through the AMS jams easily. Feed direct from the external spool holder if shore <95A."
        )

    if intent.transparent and material.name != "PETG":
        warnings.append(
            "Transparent results basically only work with PETG (and require specific settings). "
            "Other materials will look milky regardless."
        )
    elif intent.transparent and material.name == "PETG":
        rationale.append(
            "Transparency tips: 0.28mm layer, 100% flow, single thick wall, 0% infill, slow."
        )

    if intent.outdoor_use and material.name in ("PLA", "PLA+"):
        warnings.append(
            "PLA creeps in sun/heat — switch to ASA or PETG for outdoor parts."
        )

    if intent.annealed_after and material.name not in ("PA-CF", "PA", "PETG-CF", "PC"):
        warnings.append(
            f"Annealing {material.name} causes significant shrinkage/warping. "
            "Worth it for PA/PC-class; not for PLA/PETG."
        )

    return Recommendation(
        printer=printer.model,
        material=material.name,
        nozzle_mm=nozzle,
        layer_height_mm=layer_height,
        first_layer_height_mm=first_layer,
        line_width_mm=line_width,
        walls=walls,
        top_layers=top,
        bottom_layers=bottom,
        infill_pct=infill_pct,
        infill_pattern=infill_pattern,
        nozzle_temp_c=nozzle_c,
        first_layer_nozzle_temp_c=first_layer_nozzle,
        bed_temp_c=bed_c,
        first_layer_bed_temp_c=first_layer_bed,
        chamber_temp_c=chamber_c,
        outer_wall_speed_mm_s=outer,
        inner_wall_speed_mm_s=inner,
        infill_speed_mm_s=infill_speed,
        travel_speed_mm_s=travel,
        first_layer_speed_mm_s=first_layer_speed,
        max_volumetric_flow_mm3s=round(flow, 1),
        fan_pct=fan,
        first_layer_fan_pct=material.first_layer_fan_pct,
        overhang_fan_pct=overhang_fan,
        retraction_mm=retraction,
        z_hop_mm=z_hop,
        supports=supports,
        support_type=support_type,
        support_overhang_threshold_deg=support_threshold,
        brim_type=brim_type,
        brim_width_mm=brim_width,
        bed_surface=material.bed_surface,
        adaptive_layer_height=adaptive_layer,
        ironing=ironing,
        pressure_advance_calibration=pa_cal,
        flow_calibration=flow_cal,
        warnings=warnings,
        rationale=rationale,
    )
