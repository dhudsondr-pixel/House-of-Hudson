"""Bambu Lab print settings optimizer.

Public API:
    >>> from bambu_optimizer import recommend, PrintIntent
    >>> r = recommend("H2D", "PLA", PrintIntent(quality="fine", purpose="visual"))
    >>> print(r.layer_height_mm)
"""

from .materials import MATERIALS, MaterialProfile, get_material
from .optimizer import PrintIntent, Recommendation, recommend
from .printers import PRINTERS, PrinterProfile, get_printer
from .render import as_json, as_studio_overrides, as_text

__all__ = [
    "MATERIALS",
    "MaterialProfile",
    "PRINTERS",
    "PrinterProfile",
    "PrintIntent",
    "Recommendation",
    "as_json",
    "as_studio_overrides",
    "as_text",
    "get_material",
    "get_printer",
    "recommend",
]
