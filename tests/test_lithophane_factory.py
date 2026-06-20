"""Smoke tests for the lithophane frame factory.

Run with:  python -m unittest discover tests
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

from lithophane_frame_factory import (
    SAMPLE_SCENES,
    LithophaneSpec,
    build_one,
    sample_image,
    heightmap_to_solid,
    image_to_thickness,
)


# Keep meshes tiny so the suite stays fast: coarse pitch, small panel.
FAST = dict(image_width_mm=20.0, pixel_pitch_mm=1.0, frame_width_mm=4.0)


class TestLithophaneFactory(unittest.TestCase):

    def test_sample_scenes_render_grayscale(self):
        for scene in SAMPLE_SCENES:
            img = sample_image(scene, size=64)
            self.assertEqual(img.mode, "L")
            self.assertEqual(img.size, (64, 64))

    def test_unknown_scene_rejected(self):
        with self.assertRaises(ValueError):
            sample_image("not-a-scene")

    def test_dark_pixels_become_thicker(self):
        # A left-dark / right-bright split should map dark -> thick.
        arr = np.zeros((32, 32), dtype=np.uint8)
        arr[:, 16:] = 255
        img = Image.fromarray(arr, "L")
        spec = LithophaneSpec(name="split", **FAST)
        thick = image_to_thickness(img, spec)
        left = thick[:, : thick.shape[1] // 2].mean()
        right = thick[:, thick.shape[1] // 2:].mean()
        self.assertGreater(left, right)
        self.assertLessEqual(thick.max(), spec.max_thickness_mm + 1e-3)
        self.assertGreaterEqual(thick.min(), spec.min_thickness_mm - 1e-3)

    def test_frame_outstands_image(self):
        # frame_depth must be raised above the thickest image wall.
        spec = LithophaneSpec(name="x", max_thickness_mm=3.0, frame_depth_mm=2.0)
        self.assertGreater(spec.frame_depth_mm, spec.max_thickness_mm)

    def test_heightmap_solid_is_watertight(self):
        heights = np.ones((10, 12), dtype=np.float32) * 2.0
        heights[3:7, 4:9] = 1.0  # a recessed window
        mesh = heightmap_to_solid(heights, pitch=1.0)
        self.assertTrue(mesh.is_watertight)
        self.assertTrue(mesh.is_winding_consistent)
        self.assertGreater(mesh.volume, 0)

    def test_build_one_writes_valid_stl(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = LithophaneSpec(name="mountains", **FAST)
            stl = build_one(spec, Path(tmp))
            self.assertTrue(stl.exists())
            self.assertEqual(stl.name, "lithophane_mountains.stl")
            mesh = trimesh.load(str(stl))
            self.assertTrue(mesh.is_watertight)
            # Flat back: minimum z sits on the bed at 0.
            self.assertAlmostEqual(mesh.bounds[0][2], 0.0, places=3)

    def test_invert_swaps_thickness(self):
        img = sample_image("wave", size=48)
        base = image_to_thickness(img, LithophaneSpec(name="w", **FAST))
        inv = image_to_thickness(
            img, LithophaneSpec(name="w", invert=True, **FAST))
        # Inverting brightness flips which regions are thick.
        self.assertLess(np.corrcoef(base.ravel(), inv.ravel())[0, 1], 0)


if __name__ == "__main__":
    unittest.main()
