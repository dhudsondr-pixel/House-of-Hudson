"""Sanity tests for orientation + settings. Run: python -m pytest -q"""

import trimesh

from print_optimizer import analyze, rank_orientations, recommend_settings, apply_orientation


def test_box_lays_flat():
    mesh = trimesh.creation.box(extents=[40, 40, 10])
    best = rank_orientations(mesh)[0]
    oriented = apply_orientation(mesh, best)
    extents = oriented.extents
    assert extents[2] == min(extents), "Box should be oriented flat (shortest axis = Z)"
    assert best.bed_contact_area_mm2 > 0


def test_pyramid_sits_on_base():
    pyramid = trimesh.Trimesh(
        vertices=[
            [0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0],
            [5, 5, 15],
        ],
        faces=[
            [0, 1, 2], [0, 2, 3],
            [0, 4, 1], [1, 4, 2], [2, 4, 3], [3, 4, 0],
        ],
    )
    best = rank_orientations(pyramid)[0]
    oriented = apply_orientation(pyramid, best)
    bottom = oriented.bounds[0, 2]
    assert abs(bottom) < 1e-6
    assert best.bed_contact_area_mm2 >= 99


def test_settings_for_small_part_use_fine_layers():
    small = trimesh.creation.box(extents=[15, 15, 15])
    best = rank_orientations(small)[0]
    oriented = apply_orientation(small, best)
    settings = recommend_settings(oriented, best)
    assert settings.layer_height_mm <= 0.16
    assert settings.infill_percent >= 18


def test_analyze_returns_full_report():
    mesh = trimesh.creation.box(extents=[30, 30, 30])
    report = analyze(mesh)
    assert "best_orientation" in report
    assert "recommended_settings" in report
    assert len(report["alternative_orientations"]) >= 1
    assert report["input"]["triangle_count"] == 12
