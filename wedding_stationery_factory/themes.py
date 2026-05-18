"""Wedding-stationery themes.

These differ from the planner themes — wedding buyers care more about
typography mood (script vs. modern sans vs. condensed serif) and accent
color palettes than about productivity vibes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class WeddingTheme:
    slug: str
    display_name: str
    primary: tuple[float, float, float]      # large names / titles
    accent: tuple[float, float, float]       # frames, dividers, monogram ring
    text: tuple[float, float, float]         # body text
    muted: tuple[float, float, float]        # form field hint lines
    background: tuple[float, float, float]
    title_font: str        # large script/serif for couple names
    body_font: str
    small_font: str
    mood_words: tuple[str, ...]
    motif: str             # 'frame' | 'flourish' | 'monogram' | 'minimal'


THEMES: dict[str, WeddingTheme] = {
    "classic-calligraphy": WeddingTheme(
        slug="classic-calligraphy",
        display_name="Classic Calligraphy",
        primary=(0.08, 0.14, 0.28),
        accent=(0.32, 0.40, 0.55),
        text=(0.10, 0.12, 0.20),
        muted=(0.60, 0.62, 0.70),
        background=(0.985, 0.975, 0.955),
        title_font="Times-Italic",
        body_font="Times-Roman",
        small_font="Times-Italic",
        mood_words=("classic", "elegant", "timeless", "navy", "calligraphy"),
        motif="frame",
    ),
    "modern-minimalist": WeddingTheme(
        slug="modern-minimalist",
        display_name="Modern Minimalist",
        primary=(0.05, 0.05, 0.05),
        accent=(0.20, 0.20, 0.20),
        text=(0.05, 0.05, 0.05),
        muted=(0.70, 0.70, 0.70),
        background=(1.0, 1.0, 1.0),
        title_font="Helvetica-Bold",
        body_font="Helvetica",
        small_font="Helvetica",
        mood_words=("modern", "minimalist", "monochrome", "clean", "contemporary"),
        motif="minimal",
    ),
    "rustic-sage": WeddingTheme(
        slug="rustic-sage",
        display_name="Rustic Sage",
        primary=(0.36, 0.46, 0.36),
        accent=(0.55, 0.42, 0.30),
        text=(0.22, 0.28, 0.22),
        muted=(0.72, 0.76, 0.68),
        background=(0.97, 0.965, 0.93),
        title_font="Times-Italic",
        body_font="Times-Roman",
        small_font="Times-Italic",
        mood_words=("rustic", "sage green", "botanical", "earthy", "garden"),
        motif="flourish",
    ),
    "romantic-blush": WeddingTheme(
        slug="romantic-blush",
        display_name="Romantic Blush",
        primary=(0.55, 0.30, 0.36),
        accent=(0.72, 0.55, 0.30),
        text=(0.30, 0.18, 0.22),
        muted=(0.90, 0.78, 0.78),
        background=(0.995, 0.975, 0.97),
        title_font="Times-BoldItalic",
        body_font="Times-Italic",
        small_font="Times-Italic",
        mood_words=("romantic", "blush pink", "floral", "soft", "feminine"),
        motif="monogram",
    ),
    "boho-kraft": WeddingTheme(
        slug="boho-kraft",
        display_name="Boho Kraft",
        primary=(0.34, 0.22, 0.12),
        accent=(0.50, 0.36, 0.22),
        text=(0.24, 0.16, 0.08),
        muted=(0.65, 0.55, 0.40),
        background=(0.93, 0.86, 0.74),
        title_font="Times-Bold",
        body_font="Times-Roman",
        small_font="Times-Italic",
        mood_words=("boho", "kraft", "rustic", "natural", "earthy"),
        motif="flourish",
    ),
    "black-tie": WeddingTheme(
        slug="black-tie",
        display_name="Black Tie",
        primary=(0.95, 0.95, 0.93),
        accent=(0.78, 0.62, 0.30),
        text=(0.95, 0.95, 0.93),
        muted=(0.50, 0.48, 0.42),
        background=(0.06, 0.06, 0.07),
        title_font="Times-Italic",
        body_font="Times-Roman",
        small_font="Times-Italic",
        mood_words=("black tie", "formal", "glamorous", "gold", "luxe"),
        motif="frame",
    ),
}


def all_themes() -> list[WeddingTheme]:
    return list(THEMES.values())
