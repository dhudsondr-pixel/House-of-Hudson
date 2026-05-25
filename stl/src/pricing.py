"""Pricing calculator: filament cost + machine time + labor + markup → quote price."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class PricingConfig:
    # All in your local currency.
    filament_cost_per_kg: float = 25.00     # typical PLA spool
    machine_rate_per_hour: float = 0.50     # electricity + wear + amortization
    labor_rate_per_hour: float = 25.00      # what your time is worth
    setup_minutes: int = 10                 # slicing + bed prep + post-processing per job
    markup_pct: int = 40                    # margin on top of cost
    currency_symbol: str = "$"

    # For STL digital downloads (no print, no labor).
    stl_price_floor: float = 3.00
    stl_price_ceiling: float = 25.00


@dataclass
class Quote:
    filament_cost: float
    machine_cost: float
    labor_cost: float
    subtotal: float
    markup: float
    total: float
    suggested_round: float    # round to a nice number for listing
    breakdown: str            # human-readable

    def as_lines(self, symbol: str = "$") -> list[str]:
        return [
            f"Filament:        {symbol}{self.filament_cost:.2f}",
            f"Machine time:    {symbol}{self.machine_cost:.2f}",
            f"Labor:           {symbol}{self.labor_cost:.2f}",
            f"Subtotal:        {symbol}{self.subtotal:.2f}",
            f"Markup:          {symbol}{self.markup:.2f}",
            f"-" * 30,
            f"Total:           {symbol}{self.total:.2f}",
            f"Listing price:   {symbol}{self.suggested_round:.2f}  (rounded for retail)",
        ]


def _nice_round(value: float) -> float:
    """Round to the next '.99 / .49' retail-friendly tier."""
    if value < 10:
        # Nearest 0.50 (e.g., 7.50, 8.00, 8.50, 9.00) then drop to .99/.49.
        bracket = round(value * 2) / 2
        bracket = max(2.99, bracket - 0.01)
        return round(bracket, 2)
    if value < 50:
        # Nearest dollar minus 0.01.
        return max(9.99, round(value) - 0.01)
    if value < 200:
        return max(49.99, round(value / 5) * 5 - 0.01)
    return max(199.99, round(value / 10) * 10 - 0.01)


def quote_print(
    filament_weight_g: float,
    print_time_hours: float,
    cfg: PricingConfig | None = None,
) -> Quote:
    """Quote for a print-on-demand custom order."""
    cfg = cfg or PricingConfig()

    filament_cost = (filament_weight_g / 1000.0) * cfg.filament_cost_per_kg
    machine_cost = print_time_hours * cfg.machine_rate_per_hour
    labor_hours = (cfg.setup_minutes / 60.0) + 0.05 * print_time_hours  # ~3 min per print hour
    labor_cost = labor_hours * cfg.labor_rate_per_hour

    subtotal = filament_cost + machine_cost + labor_cost
    markup = subtotal * (cfg.markup_pct / 100.0)
    total = subtotal + markup
    suggested = _nice_round(total)

    breakdown = (
        f"Filament: {filament_weight_g:.0f}g @ {cfg.currency_symbol}{cfg.filament_cost_per_kg:.0f}/kg "
        f"= {cfg.currency_symbol}{filament_cost:.2f}\n"
        f"Machine:  {print_time_hours:.1f}h @ {cfg.currency_symbol}{cfg.machine_rate_per_hour:.2f}/h "
        f"= {cfg.currency_symbol}{machine_cost:.2f}\n"
        f"Labor:    {labor_hours:.2f}h @ {cfg.currency_symbol}{cfg.labor_rate_per_hour:.0f}/h "
        f"= {cfg.currency_symbol}{labor_cost:.2f}\n"
        f"Markup:   {cfg.markup_pct}% on subtotal = {cfg.currency_symbol}{markup:.2f}"
    )

    return Quote(
        filament_cost=filament_cost,
        machine_cost=machine_cost,
        labor_cost=labor_cost,
        subtotal=subtotal,
        markup=markup,
        total=total,
        suggested_round=suggested,
        breakdown=breakdown,
    )


def suggest_stl_price(
    bbox_mm: tuple[float, float, float],
    triangle_count: int,
    complexity: str = "auto",
    cfg: PricingConfig | None = None,
) -> Dict[str, float]:
    """Suggest pricing for the digital STL file across platforms.

    Returns a dict like:
        {"cults3d": 4.99, "etsy": 5.99, "patreon_tier": 5.00, ...}
    Uses size and triangle count as rough complexity signals.
    """
    cfg = cfg or PricingConfig()

    size_factor = max(bbox_mm) / 100.0  # 0.5 for 50mm, 1.0 for 100mm, 2.5 for 250mm
    complexity_factor = min(2.5, max(0.5, triangle_count / 50000))

    if complexity == "simple":
        complexity_factor *= 0.7
    elif complexity == "intricate":
        complexity_factor *= 1.4

    base = 3.0 + (size_factor + complexity_factor) * 2.5
    base = max(cfg.stl_price_floor, min(cfg.stl_price_ceiling, base))

    # Platform-specific adjustments.
    cults = _nice_round(base)
    etsy = _nice_round(base * 1.2)       # Etsy buyers expect slightly higher; covers fees
    patreon = round(base / 2) if base > 6 else 3  # monthly tier slot
    makerworld = 0.0   # MakerWorld doesn't sell — free uploads earn points
    printables = 0.0   # same
    thingiverse = 0.0  # free
    direct_site = _nice_round(base * 1.1)

    return {
        "cults3d": cults,
        "etsy": etsy,
        "patreon_monthly_tier": float(patreon),
        "makerworld": makerworld,
        "printables": printables,
        "thingiverse": thingiverse,
        "direct_site": direct_site,
    }
