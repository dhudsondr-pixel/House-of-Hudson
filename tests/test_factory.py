"""Smoke tests for the Etsy planner factory.

Run with:  python -m unittest discover tests
"""

import tempfile
import unittest
from pathlib import Path

from etsy_planner_factory import (
    PLANNER_TYPES,
    THEMES,
    all_combinations,
    build_listing,
    build_one,
)
from etsy_planner_factory.factory import ProductSpec


class TestFactory(unittest.TestCase):

    def test_36_combinations(self):
        combos = all_combinations()
        self.assertEqual(len(combos), len(PLANNER_TYPES) * len(THEMES))
        self.assertEqual(len(combos), 36)

    def test_build_one_produces_all_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = build_one(
                ProductSpec(planner_slug="daily-planner",
                            theme_slug="sage-botanical"),
                root,
            )
            for expected in [
                "product.pdf",
                "image-1-hero.png",
                "image-2-preview.png",
                "image-3-card.png",
                "listing.txt",
            ]:
                self.assertTrue(
                    (folder / expected).exists(),
                    f"missing {expected}",
                )
                self.assertGreater((folder / expected).stat().st_size, 100)

    def test_every_planner_x_theme_combo_renders(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for spec in all_combinations():
                folder = build_one(spec, root)
                self.assertTrue((folder / "product.pdf").exists())

    def test_listing_respects_etsy_limits(self):
        for slug, p in PLANNER_TYPES.items():
            for theme_slug, theme in THEMES.items():
                l = build_listing(
                    p["display_name"],
                    p["keywords"],
                    theme,
                    sku=f"{slug}__{theme_slug}",
                )
                self.assertLessEqual(len(l.title), 140, msg=l.title)
                self.assertEqual(len(l.tags), 13)
                for tag in l.tags:
                    self.assertLessEqual(len(tag), 20, msg=tag)
                self.assertGreater(l.suggested_price_usd, 0)
                self.assertGreater(len(l.description), 200)


if __name__ == "__main__":
    unittest.main()
