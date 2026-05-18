"""Visual theme definitions for printable planners.

Each theme is a coordinated palette + typography combination. Etsy buyers
shop visually — listing the same planner in 5 themes effectively gives you
5 listings from one design.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    slug: str
    display_name: str
    primary: tuple[float, float, float]      # accent / header bars
    secondary: tuple[float, float, float]    # subheads / dividers
    text: tuple[float, float, float]
    muted: tuple[float, float, float]        # checkbox outlines, light lines
    background: tuple[float, float, float]
    header_font: str
    body_font: str
    mood_words: tuple[str, ...]              # used in listing copy


THEMES: dict[str, Theme] = {
    "minimalist-mono": Theme(
        slug="minimalist-mono",
        display_name="Minimalist Mono",
        primary=(0.10, 0.10, 0.10),
        secondary=(0.35, 0.35, 0.35),
        text=(0.10, 0.10, 0.10),
        muted=(0.78, 0.78, 0.78),
        background=(1.0, 1.0, 1.0),
        header_font="Helvetica-Bold",
        body_font="Helvetica",
        mood_words=("minimalist", "clean", "simple", "modern", "monochrome"),
    ),
    "sage-botanical": Theme(
        slug="sage-botanical",
        display_name="Sage Botanical",
        primary=(0.40, 0.52, 0.40),
        secondary=(0.62, 0.70, 0.58),
        text=(0.20, 0.27, 0.20),
        muted=(0.80, 0.84, 0.78),
        background=(0.985, 0.985, 0.97),
        header_font="Times-Bold",
        body_font="Times-Roman",
        mood_words=("sage green", "botanical", "natural", "earthy", "calm"),
    ),
    "blush-floral": Theme(
        slug="blush-floral",
        display_name="Blush",
        primary=(0.78, 0.50, 0.55),
        secondary=(0.88, 0.72, 0.74),
        text=(0.30, 0.18, 0.22),
        muted=(0.93, 0.85, 0.86),
        background=(0.995, 0.97, 0.97),
        header_font="Times-Bold",
        body_font="Times-Roman",
        mood_words=("blush pink", "feminine", "floral", "soft", "romantic"),
    ),
    "dark-mode": Theme(
        slug="dark-mode",
        display_name="Dark Mode",
        primary=(0.95, 0.95, 0.95),
        secondary=(0.65, 0.65, 0.70),
        text=(0.95, 0.95, 0.95),
        muted=(0.45, 0.45, 0.50),
        background=(0.10, 0.10, 0.12),
        header_font="Helvetica-Bold",
        body_font="Helvetica",
        mood_words=("dark mode", "moody", "modern", "dramatic", "tech"),
    ),
    "kraft-paper": Theme(
        slug="kraft-paper",
        display_name="Kraft Paper",
        primary=(0.36, 0.24, 0.14),
        secondary=(0.55, 0.40, 0.25),
        text=(0.25, 0.18, 0.10),
        muted=(0.75, 0.65, 0.50),
        background=(0.94, 0.88, 0.76),
        header_font="Times-Bold",
        body_font="Times-Roman",
        mood_words=("kraft paper", "rustic", "vintage", "warm", "cozy"),
    ),
    "navy-classic": Theme(
        slug="navy-classic",
        display_name="Navy Classic",
        primary=(0.10, 0.18, 0.36),
        secondary=(0.30, 0.40, 0.58),
        text=(0.08, 0.14, 0.28),
        muted=(0.80, 0.83, 0.90),
        background=(0.99, 0.99, 1.0),
        header_font="Helvetica-Bold",
        body_font="Helvetica",
        mood_words=("navy", "classic", "professional", "executive", "academic"),
    ),
}


def all_themes() -> list[Theme]:
    return list(THEMES.values())


def get_theme(slug: str) -> Theme:
    return THEMES[slug]
