"""Deterministic, versioned emission-factor lookup tables.

Every factor is expressed as kg CO2e per the stated canonical unit. The
calculation pipeline (`app/services/emission_calculation_service.py`) assumes
the user-entered `unit` on `EnergyConsumption` / `Material` / `Waste` already
matches the canonical unit below -- no unit conversion is performed in this
step (documented hackathon-scope limitation, see Step 05 spec).

Each factor carries a `source` and `version` for traceability (PRD Risk 1).
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class EmissionFactor:
    """A single emission factor with full source/version traceability."""

    factor: Decimal
    """kg CO2e per canonical `unit`."""

    unit: str
    """Canonical unit this factor is defined for."""

    source: str
    """Human-readable citation for the factor's origin."""

    version: str
    """Version / effective-date tag for the factor value."""


# --- Energy factors, keyed by `EnergyConsumption.energy_type` ---
# Matches the `EnergyType` literal in `app/schemas/energy_consumption.py`.
ENERGY_EMISSION_FACTORS: dict[str, EmissionFactor] = {
    "electricity": EmissionFactor(
        factor=Decimal("0.71"),
        unit="kWh",
        source="CEA CO2 Baseline Database for the Indian Power Sector, grid average emission factor",
        version="v19 (2024)",
    ),
    "natural_gas": EmissionFactor(
        factor=Decimal("2.02"),
        unit="m3",
        source="IPCC 2006 Guidelines for National GHG Inventories, Vol. 2, Table 1.4 (natural gas, default)",
        version="2006",
    ),
    "diesel": EmissionFactor(
        factor=Decimal("2.68"),
        unit="L",
        source="IPCC 2006 Guidelines for National GHG Inventories, Vol. 2, Table 1.4 (gas/diesel oil, default)",
        version="2006",
    ),
    "coal": EmissionFactor(
        factor=Decimal("2.42"),
        unit="kg",
        source="IPCC 2006 Guidelines for National GHG Inventories, Vol. 2, Table 1.4 (other bituminous coal, default)",
        version="2006",
    ),
    "renewable_electricity": EmissionFactor(
        factor=Decimal("0.00"),
        unit="kWh",
        source="GHG Protocol Scope 2 Guidance, market-based method (zero-rated certified renewable electricity)",
        version="2015",
    ),
    "other": EmissionFactor(
        factor=Decimal("0.50"),
        unit="kWh",
        source="Generic placeholder factor for unspecified/other energy types (hackathon MVP default)",
        version="2024",
    ),
}

# --- Material factors ---
# Per the Step 05 spec, every material uses one generic virgin/recycled factor
# pair, independent of the free-text `material_name`. A per-material-name
# factor table is out of scope for this hackathon MVP.
MATERIAL_VIRGIN_FACTOR = EmissionFactor(
    factor=Decimal("2.00"),
    unit="kg",
    source="Generic virgin-material average factor (hackathon MVP placeholder, ecoinvent-style order-of-magnitude average)",
    version="2024",
)

MATERIAL_RECYCLED_FACTOR = EmissionFactor(
    factor=Decimal("0.50"),
    unit="kg",
    source="Generic recycled-material average factor (hackathon MVP placeholder, ecoinvent-style order-of-magnitude average)",
    version="2024",
)

# --- Waste factors, keyed by `Waste.disposal_method` ---
# Matches the `DisposalMethod` literal in `app/schemas/waste.py`.
WASTE_DISPOSAL_FACTORS: dict[str, EmissionFactor] = {
    "landfilled": EmissionFactor(
        factor=Decimal("0.58"),
        unit="kg",
        source="IPCC 2006 Guidelines for National GHG Inventories, Vol. 5, Ch. 3 (solid waste disposal, default)",
        version="2006",
    ),
    "recycled": EmissionFactor(
        factor=Decimal("0.05"),
        unit="kg",
        source="Generic low-impact factor for recycled waste streams (hackathon MVP placeholder)",
        version="2024",
    ),
    "reused": EmissionFactor(
        factor=Decimal("0.02"),
        unit="kg",
        source="Generic low-impact factor for reused waste streams (hackathon MVP placeholder)",
        version="2024",
    ),
    "sold": EmissionFactor(
        factor=Decimal("0.05"),
        unit="kg",
        source="Generic low-impact factor for sold-as-byproduct waste streams (hackathon MVP placeholder)",
        version="2024",
    ),
    "other": EmissionFactor(
        factor=Decimal("0.30"),
        unit="kg",
        source="Generic placeholder factor for unspecified disposal methods (hackathon MVP default)",
        version="2024",
    ),
}


def emission_factor_citation(entry: EmissionFactor) -> str:
    """Build a single traceable citation string for `EmissionResult.emission_factor_source`."""

    return f"{entry.source} ({entry.version})"
