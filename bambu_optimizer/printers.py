"""Printer capability profiles.

Verified models: A1, H2D.
Unverified models included as best-effort placeholders so callers can still
exercise the optimizer end-to-end. Edit the numbers if your hardware differs.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PrinterProfile:
    model: str
    build_volume_mm: tuple[int, int, int]
    nozzle_sizes_mm: tuple[float, ...]
    default_nozzle_mm: float
    max_hotend_c: int
    max_bed_c: int
    enclosed: bool
    chamber_heater: bool
    ams_supported: bool
    multi_color: bool
    dual_extruder: bool
    max_volumetric_flow_mm3s: float  # rated, generic PLA
    max_travel_speed_mm_s: int
    max_print_accel_mm_s2: int
    has_lidar: bool
    has_camera: bool
    notes: str = ""
    verified: bool = True


PRINTERS: dict[str, PrinterProfile] = {
    "A1": PrinterProfile(
        model="A1",
        build_volume_mm=(256, 256, 256),
        nozzle_sizes_mm=(0.2, 0.4, 0.6, 0.8),
        default_nozzle_mm=0.4,
        max_hotend_c=300,
        max_bed_c=100,
        enclosed=False,
        chamber_heater=False,
        ams_supported=True,  # AMS lite
        multi_color=True,
        dual_extruder=False,
        max_volumetric_flow_mm3s=28.0,
        max_travel_speed_mm_s=500,
        max_print_accel_mm_s2=10000,
        has_lidar=False,
        has_camera=True,
        notes="Bedslinger; avoid tall/narrow parts at high speed. No enclosure so ABS/ASA/PC discouraged.",
    ),
    "H2D": PrinterProfile(
        model="H2D",
        build_volume_mm=(325, 320, 325),
        nozzle_sizes_mm=(0.2, 0.4, 0.6, 0.8),
        default_nozzle_mm=0.4,
        max_hotend_c=320,
        max_bed_c=110,
        enclosed=True,
        chamber_heater=True,
        ams_supported=True,
        multi_color=True,
        dual_extruder=True,
        max_volumetric_flow_mm3s=32.0,
        max_travel_speed_mm_s=1000,
        max_print_accel_mm_s2=20000,
        has_lidar=True,
        has_camera=True,
        notes="Dual-extruder, actively heated chamber. Best choice for engineering filaments and multi-material parts.",
    ),
    # Below: unverified placeholders. Treat numbers as starting points.
    "H2C": PrinterProfile(
        model="H2C",
        build_volume_mm=(325, 320, 325),
        nozzle_sizes_mm=(0.2, 0.4, 0.6, 0.8),
        default_nozzle_mm=0.4,
        max_hotend_c=320,
        max_bed_c=110,
        enclosed=True,
        chamber_heater=True,
        ams_supported=True,
        multi_color=True,
        dual_extruder=False,
        max_volumetric_flow_mm3s=32.0,
        max_travel_speed_mm_s=1000,
        max_print_accel_mm_s2=20000,
        has_lidar=True,
        has_camera=True,
        notes="UNVERIFIED MODEL: settings assume an H2D-class single-extruder variant.",
        verified=False,
    ),
    "P2S": PrinterProfile(
        model="P2S",
        build_volume_mm=(256, 256, 256),
        nozzle_sizes_mm=(0.2, 0.4, 0.6, 0.8),
        default_nozzle_mm=0.4,
        max_hotend_c=300,
        max_bed_c=100,
        enclosed=True,
        chamber_heater=False,
        ams_supported=True,
        multi_color=True,
        dual_extruder=False,
        max_volumetric_flow_mm3s=30.0,
        max_travel_speed_mm_s=500,
        max_print_accel_mm_s2=20000,
        has_lidar=False,
        has_camera=True,
        notes="UNVERIFIED MODEL: settings assume a P1S successor. Did you mean P1S?",
        verified=False,
    ),
    "X2D": PrinterProfile(
        model="X2D",
        build_volume_mm=(256, 256, 256),
        nozzle_sizes_mm=(0.2, 0.4, 0.6, 0.8),
        default_nozzle_mm=0.4,
        max_hotend_c=320,
        max_bed_c=110,
        enclosed=True,
        chamber_heater=False,
        ams_supported=True,
        multi_color=True,
        dual_extruder=False,
        max_volumetric_flow_mm3s=32.0,
        max_travel_speed_mm_s=600,
        max_print_accel_mm_s2=20000,
        has_lidar=True,
        has_camera=True,
        notes="UNVERIFIED MODEL: settings assume an X1C-class successor. Did you mean X1C?",
        verified=False,
    ),
}


def get_printer(name: str) -> PrinterProfile:
    key = name.strip().upper()
    if key not in PRINTERS:
        raise KeyError(
            f"Unknown printer '{name}'. Available: {', '.join(PRINTERS)}"
        )
    return PRINTERS[key]
