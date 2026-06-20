"""Lithophane Frame Factory.

Turn any photo into a 3D-printable *framed lithophane* — a thin translucent
panel whose thickness varies with image brightness, so the picture only
appears when light shines through it from behind. A raised border frames the
image, and the back is flat so it prints on a Bambu with no supports.

Public API:
    SAMPLE_SCENES      names of the built-in procedural demo images
    LithophaneSpec     parameters for one lithophane (size, frame, thickness)
    build_one          generate STL + preview for one image
    sample_image       procedurally render a built-in demo image
"""

from .generate import (
    SAMPLE_SCENES,
    LithophaneSpec,
    build_one,
    sample_image,
    heightmap_to_solid,
    image_to_thickness,
)

__all__ = [
    "SAMPLE_SCENES",
    "LithophaneSpec",
    "build_one",
    "sample_image",
    "heightmap_to_solid",
    "image_to_thickness",
]
