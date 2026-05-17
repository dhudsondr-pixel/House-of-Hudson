"""Output formatters: human-readable report, JSON, and Bambu Studio overrides."""

import json
from .optimizer import Recommendation


def as_text(r: Recommendation) -> str:
    lines = []
    lines.append(f"=== Bambu print plan: {r.printer} / {r.material} / {r.nozzle_mm}mm nozzle ===\n")

    lines.append("[Geometry]")
    lines.append(f"  layer height            {r.layer_height_mm} mm")
    lines.append(f"  first layer height      {r.first_layer_height_mm} mm")
    lines.append(f"  line width              {r.line_width_mm} mm")
    lines.append(f"  walls / top / bottom    {r.walls} / {r.top_layers} / {r.bottom_layers}")
    lines.append(f"  infill                  {r.infill_pct}% {r.infill_pattern}")
    lines.append("")

    lines.append("[Temperatures]")
    lines.append(f"  nozzle                  {r.nozzle_temp_c}C  (first layer {r.first_layer_nozzle_temp_c}C)")
    lines.append(f"  bed                     {r.bed_temp_c}C  (first layer {r.first_layer_bed_temp_c}C)")
    if r.chamber_temp_c:
        lines.append(f"  chamber                 {r.chamber_temp_c}C")
    lines.append("")

    lines.append("[Speeds]")
    lines.append(f"  outer wall              {r.outer_wall_speed_mm_s} mm/s")
    lines.append(f"  inner wall              {r.inner_wall_speed_mm_s} mm/s")
    lines.append(f"  infill                  {r.infill_speed_mm_s} mm/s")
    lines.append(f"  travel                  {r.travel_speed_mm_s} mm/s")
    lines.append(f"  first layer             {r.first_layer_speed_mm_s} mm/s")
    lines.append(f"  max volumetric flow     {r.max_volumetric_flow_mm3s} mm^3/s")
    lines.append("")

    lines.append("[Cooling]")
    lines.append(f"  part fan                {r.fan_pct}%")
    lines.append(f"  first layer fan         {r.first_layer_fan_pct}%")
    lines.append(f"  overhang fan            {r.overhang_fan_pct}%")
    lines.append("")

    lines.append("[Retraction]")
    lines.append(f"  distance                {r.retraction_mm} mm")
    lines.append(f"  z-hop                   {r.z_hop_mm} mm")
    lines.append("")

    lines.append("[Adhesion]")
    lines.append(f"  bed surface             {r.bed_surface}")
    lines.append(f"  brim                    {r.brim_type} ({r.brim_width_mm} mm)")
    lines.append("")

    lines.append("[Supports]")
    if r.supports:
        lines.append(f"  enabled                 yes ({r.support_type})")
        lines.append(f"  overhang threshold      {r.support_overhang_threshold_deg} deg")
    else:
        lines.append("  enabled                 no")
    lines.append("")

    lines.append("[Quality]")
    lines.append(f"  adaptive layer height   {'on' if r.adaptive_layer_height else 'off'}")
    lines.append(f"  ironing                 {'on (top surface)' if r.ironing else 'off'}")
    lines.append("")

    lines.append("[Calibration]")
    lines.append(f"  pressure advance        {r.pressure_advance_calibration}")
    lines.append(f"  flow rate               {r.flow_calibration}")

    if r.rationale:
        lines.append("\n[Rationale]")
        for note in r.rationale:
            lines.append(f"  - {note}")

    if r.warnings:
        lines.append("\n[!] Warnings")
        for w in r.warnings:
            lines.append(f"  - {w}")

    return "\n".join(lines)


def as_json(r: Recommendation) -> str:
    return json.dumps(r.to_dict(), indent=2)


def as_studio_overrides(r: Recommendation) -> str:
    """A flat key=value list of the keys most users tweak in Bambu Studio.

    Useful as a paste-target into a custom process profile.
    """
    pairs = {
        "layer_height": r.layer_height_mm,
        "initial_layer_print_height": r.first_layer_height_mm,
        "line_width": r.line_width_mm,
        "wall_loops": r.walls,
        "top_shell_layers": r.top_layers,
        "bottom_shell_layers": r.bottom_layers,
        "sparse_infill_density": f"{r.infill_pct}%",
        "sparse_infill_pattern": r.infill_pattern,
        "nozzle_temperature": r.nozzle_temp_c,
        "nozzle_temperature_initial_layer": r.first_layer_nozzle_temp_c,
        "hot_plate_temp": r.bed_temp_c,
        "hot_plate_temp_initial_layer": r.first_layer_bed_temp_c,
        "outer_wall_speed": r.outer_wall_speed_mm_s,
        "inner_wall_speed": r.inner_wall_speed_mm_s,
        "sparse_infill_speed": r.infill_speed_mm_s,
        "travel_speed": r.travel_speed_mm_s,
        "initial_layer_speed": r.first_layer_speed_mm_s,
        "filament_max_volumetric_speed": r.max_volumetric_flow_mm3s,
        "fan_max_speed": r.fan_pct,
        "overhang_fan_speed": r.overhang_fan_pct,
        "retraction_length": r.retraction_mm,
        "z_hop": r.z_hop_mm,
        "enable_support": "1" if r.supports else "0",
        "support_threshold_angle": r.support_overhang_threshold_deg,
        "brim_type": r.brim_type,
        "brim_width": r.brim_width_mm,
        "adaptive_layer_height": "1" if r.adaptive_layer_height else "0",
        "ironing_type": "top" if r.ironing else "no_ironing",
    }
    return "\n".join(f"{k} = {v}" for k, v in pairs.items())
