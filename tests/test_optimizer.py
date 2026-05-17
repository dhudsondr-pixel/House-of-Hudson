"""Sanity tests. Run from repo root with: python -m unittest discover tests"""

import unittest

from bambu_optimizer import PRINTERS, PrintIntent, recommend
from bambu_optimizer.render import as_json, as_studio_overrides, as_text


class TestRecommend(unittest.TestCase):
    def test_every_printer_runs(self):
        for name in PRINTERS:
            r = recommend(name, "PLA", PrintIntent())
            self.assertGreater(r.layer_height_mm, 0)
            self.assertGreater(r.outer_wall_speed_mm_s, 0)
            self.assertGreaterEqual(r.bed_temp_c, 0)

    def test_warns_open_printer_with_engineering_filament(self):
        r = recommend("A1", "ABS", PrintIntent())
        self.assertTrue(any("enclos" in w.lower() for w in r.warnings))

    def test_dual_extruder_h2d_uses_dissolvable_supports(self):
        r = recommend("H2D", "PLA", PrintIntent(has_overhangs=True))
        self.assertTrue(r.supports)
        self.assertIn("dual", r.support_type.lower() + " ".join(r.rationale).lower())

    def test_unverified_printer_gets_flag(self):
        r = recommend("H2C", "PLA", PrintIntent())
        self.assertTrue(any("unverified" in w.lower() for w in r.warnings))

    def test_pacf_requires_hardened_nozzle_warning(self):
        r = recommend("H2D", "PA-CF", PrintIntent(purpose="mechanical"))
        self.assertTrue(any("hardened" in w.lower() for w in r.warnings))
        self.assertEqual(r.infill_pct, 60)

    def test_quality_affects_layer_height(self):
        draft = recommend("H2D", "PLA", PrintIntent(quality="draft")).layer_height_mm
        fine = recommend("H2D", "PLA", PrintIntent(quality="fine")).layer_height_mm
        self.assertGreater(draft, fine)

    def test_volumetric_flow_caps_speed(self):
        # A1 has ~28 mm^3/s; at 0.2mm layer & 0.45mm width, cap ~ 311 mm/s.
        r = recommend("A1", "PLA", PrintIntent(quality="draft"))
        self.assertLessEqual(r.outer_wall_speed_mm_s, 400)

    def test_renderers_produce_strings(self):
        r = recommend("H2D", "PETG", PrintIntent())
        self.assertIn("Bambu print plan", as_text(r))
        self.assertIn("layer_height", as_studio_overrides(r))
        self.assertIn('"layer_height_mm"', as_json(r))


if __name__ == "__main__":
    unittest.main()
