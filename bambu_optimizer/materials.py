"""Filament material profiles.

Values are conservative starting points pulled from Bambu's published generic
profiles. The optimizer further tunes them based on printer capabilities and
the user's quality target.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialProfile:
    name: str
    nozzle_c: tuple[int, int]      # (min, max) recommended hotend temp
    bed_c: tuple[int, int]         # (min, max) bed temp
    chamber_c: int                 # 0 means ambient is fine
    requires_enclosure: bool
    fan_pct: int                   # part-cooling fan percentage (steady state)
    first_layer_fan_pct: int
    base_volumetric_flow_mm3s: float
    base_speed_mm_s: int           # outer-wall reference speed
    retraction_mm: float
    shrinkage_pct: float
    warps: bool
    abrasive: bool
    bed_surface: str
    adhesion_aid: str
    drying_c: int                  # 0 means no drying needed
    drying_hours: int
    notes: str


MATERIALS: dict[str, MaterialProfile] = {
    "PLA": MaterialProfile(
        name="PLA",
        nozzle_c=(210, 230),
        bed_c=(55, 65),
        chamber_c=0,
        requires_enclosure=False,
        fan_pct=100,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=20.0,
        base_speed_mm_s=200,
        retraction_mm=0.8,
        shrinkage_pct=0.3,
        warps=False,
        abrasive=False,
        bed_surface="Textured PEI or Cool Plate",
        adhesion_aid="None",
        drying_c=45,
        drying_hours=6,
        notes="Open the door on enclosed printers to avoid heat creep.",
    ),
    "PLA+": MaterialProfile(
        name="PLA+",
        nozzle_c=(215, 235),
        bed_c=(55, 65),
        chamber_c=0,
        requires_enclosure=False,
        fan_pct=80,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=22.0,
        base_speed_mm_s=220,
        retraction_mm=0.8,
        shrinkage_pct=0.3,
        warps=False,
        abrasive=False,
        bed_surface="Textured PEI",
        adhesion_aid="None",
        drying_c=45,
        drying_hours=6,
        notes="Tougher than standard PLA; great default for functional parts that stay <50C.",
    ),
    "PETG": MaterialProfile(
        name="PETG",
        nozzle_c=(240, 260),
        bed_c=(70, 80),
        chamber_c=0,
        requires_enclosure=False,
        fan_pct=50,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=14.0,
        base_speed_mm_s=150,
        retraction_mm=1.0,
        shrinkage_pct=0.4,
        warps=False,
        abrasive=False,
        bed_surface="Textured PEI (NOT smooth PEI — it WILL chip)",
        adhesion_aid="Glue stick as release agent on smooth PEI",
        drying_c=65,
        drying_hours=6,
        notes="Strings if wet. Dry first if you see whiskers.",
    ),
    "ABS": MaterialProfile(
        name="ABS",
        nozzle_c=(250, 270),
        bed_c=(90, 100),
        chamber_c=45,
        requires_enclosure=True,
        fan_pct=0,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=15.0,
        base_speed_mm_s=180,
        retraction_mm=0.8,
        shrinkage_pct=0.8,
        warps=True,
        abrasive=False,
        bed_surface="Engineering plate or smooth PEI",
        adhesion_aid="Glue stick; brim 5mm for parts >100mm long",
        drying_c=65,
        drying_hours=4,
        notes="Ventilation matters: styrene fumes.",
    ),
    "ASA": MaterialProfile(
        name="ASA",
        nozzle_c=(250, 270),
        bed_c=(90, 100),
        chamber_c=45,
        requires_enclosure=True,
        fan_pct=0,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=14.0,
        base_speed_mm_s=180,
        retraction_mm=0.8,
        shrinkage_pct=0.7,
        warps=True,
        abrasive=False,
        bed_surface="Engineering plate or smooth PEI",
        adhesion_aid="Glue stick; brim for tall/narrow parts",
        drying_c=65,
        drying_hours=4,
        notes="UV-stable replacement for ABS; same enclosure rules.",
    ),
    "PC": MaterialProfile(
        name="PC",
        nozzle_c=(270, 290),
        bed_c=(100, 110),
        chamber_c=60,
        requires_enclosure=True,
        fan_pct=0,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=12.0,
        base_speed_mm_s=150,
        retraction_mm=0.8,
        shrinkage_pct=0.8,
        warps=True,
        abrasive=False,
        bed_surface="Engineering plate",
        adhesion_aid="Magigoo PC or glue stick; brim recommended",
        drying_c=80,
        drying_hours=8,
        notes="Must be bone dry — PC is hygroscopic and gets brittle if printed wet.",
    ),
    "PA-CF": MaterialProfile(
        name="PA-CF",
        nozzle_c=(280, 300),
        bed_c=(80, 90),
        chamber_c=55,
        requires_enclosure=True,
        fan_pct=20,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=10.0,
        base_speed_mm_s=120,
        retraction_mm=1.0,
        shrinkage_pct=0.9,
        warps=True,
        abrasive=True,
        bed_surface="Engineering plate",
        adhesion_aid="Glue stick; brim mandatory",
        drying_c=80,
        drying_hours=12,
        notes="Hardened steel nozzle REQUIRED. Anneal at 80C/4h for full strength.",
    ),
    "PA": MaterialProfile(
        name="PA",
        nozzle_c=(270, 290),
        bed_c=(80, 90),
        chamber_c=55,
        requires_enclosure=True,
        fan_pct=10,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=10.0,
        base_speed_mm_s=120,
        retraction_mm=1.0,
        shrinkage_pct=1.2,
        warps=True,
        abrasive=False,
        bed_surface="Engineering plate",
        adhesion_aid="Glue stick; brim mandatory",
        drying_c=80,
        drying_hours=12,
        notes="Extremely hygroscopic — dry within the print session.",
    ),
    "PETG-CF": MaterialProfile(
        name="PETG-CF",
        nozzle_c=(250, 270),
        bed_c=(70, 80),
        chamber_c=0,
        requires_enclosure=False,
        fan_pct=40,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=12.0,
        base_speed_mm_s=150,
        retraction_mm=1.0,
        shrinkage_pct=0.5,
        warps=False,
        abrasive=True,
        bed_surface="Textured PEI",
        adhesion_aid="None",
        drying_c=65,
        drying_hours=6,
        notes="Hardened steel nozzle REQUIRED. Stiff but brittle.",
    ),
    "TPU": MaterialProfile(
        name="TPU",
        nozzle_c=(220, 240),
        bed_c=(35, 50),
        chamber_c=0,
        requires_enclosure=False,
        fan_pct=60,
        first_layer_fan_pct=0,
        base_volumetric_flow_mm3s=6.0,
        base_speed_mm_s=40,
        retraction_mm=0.4,
        shrinkage_pct=0.5,
        warps=False,
        abrasive=False,
        bed_surface="Textured PEI",
        adhesion_aid="None — and DO NOT use glue, parts will fuse to the plate",
        drying_c=50,
        drying_hours=8,
        notes="Slow down and minimize retraction. Avoid AMS on shore <95A.",
    ),
}


def get_material(name: str) -> MaterialProfile:
    key = name.strip().upper().replace(" ", "")
    if key not in MATERIALS:
        raise KeyError(
            f"Unknown material '{name}'. Available: {', '.join(MATERIALS)}"
        )
    return MATERIALS[key]
