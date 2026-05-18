"""Smoke tests for the wedding stationery factory."""

import tempfile
import unittest
from pathlib import Path

from wedding_stationery_factory import (
    CARD_TYPES,
    THEMES,
    all_combinations,
    build_listing,
    build_one,
)
from wedding_stationery_factory.factory import ProductSpec


class TestWeddingFactory(unittest.TestCase):

    def test_36_combinations(self):
        self.assertEqual(len(all_combinations()),
                         len(CARD_TYPES) * len(THEMES))
        self.assertEqual(len(all_combinations()), 36)

    def test_build_one_produces_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = build_one(
                ProductSpec(card_slug="invitation",
                            theme_slug="classic-calligraphy"),
                Path(tmp),
            )
            for f in ("product.pdf", "image-1-hero.png",
                      "image-2-card.png", "image-3-features.png",
                      "listing.txt"):
                p = folder / f
                self.assertTrue(p.exists(), f"missing {f}")
                self.assertGreater(p.stat().st_size, 100)

    def test_preview_pdf_is_cleaned_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = build_one(
                ProductSpec(card_slug="save-the-date",
                            theme_slug="rustic-sage"),
                Path(tmp),
            )
            # The internal preview PDF should be deleted; only product.pdf
            # remains for the customer.
            self.assertFalse((folder / "_preview.pdf").exists())
            self.assertTrue((folder / "product.pdf").exists())

    def test_every_combination_renders(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for spec in all_combinations():
                build_one(spec, root)

    def test_listings_respect_etsy_limits(self):
        for cslug, c in CARD_TYPES.items():
            for tslug, t in THEMES.items():
                l = build_listing(
                    card_display_name=c["display_name"],
                    card_keywords=c["keywords"],
                    card_size_label=c["size"],
                    theme=t,
                    sku=f"{cslug}__{tslug}",
                )
                self.assertLessEqual(len(l.title), 140, l.title)
                self.assertEqual(len(l.tags), 13)
                for tag in l.tags:
                    self.assertLessEqual(len(tag), 20, tag)
                self.assertGreater(l.suggested_price_usd, 0)

    def test_invitation_priced_higher_than_rsvp(self):
        # Sanity: invitations are the centerpiece and cost ~2x RSVP.
        theme = THEMES["classic-calligraphy"]
        inv = build_listing("Wedding Invitation",
                            CARD_TYPES["invitation"]["keywords"],
                            "5x7", theme, "test")
        rsvp = build_listing("RSVP Card",
                             CARD_TYPES["rsvp-card"]["keywords"],
                             "5x3.5", theme, "test")
        self.assertGreater(inv.suggested_price_usd,
                           rsvp.suggested_price_usd)


if __name__ == "__main__":
    unittest.main()
