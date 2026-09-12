"""Deterministic, versioned mapping from hotspot `(category, activity)` to a
fixed set of candidate circular-economy interventions.

Every candidate carries fixed, documented values -- nothing is invented at
call time (per PRD §13 / Step 06 spec "Scoring determinism rules"). Each
candidate is either:

- a **factor-swap** candidate: `alt_factor` points at the alternate
  `EmissionFactor` entry in `app/data/emission_factors.py` that the
  recommendation would move the activity to (e.g. `landfilled` waste ->
  `recycled` waste, virgin material -> recycled material, grid electricity ->
  renewable electricity). `co2_reduction` is computed by
  `recommendation_service` as
  `hotspot.co2e - (hotspot.co2e / hotspot.emission_factor) * alt_factor.factor`.
- a **fixed-percentage** candidate: `reduction_percentage` is a fixed,
  documented percentage (e.g. 8% per PRD §12 example) applied directly to the
  hotspot's `co2e`. Used for `reduce` / `process_optimization` candidates
  that have no natural factor-table swap (pure consumption/process
  efficiency improvements).

Every candidate has exactly one of `alt_factor` / `reduction_percentage` set.

`title` / `description` are templates that `recommendation_service` formats
with `activity=hotspot.activity`.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from app.data.emission_factors import (
    ENERGY_EMISSION_FACTORS,
    MATERIAL_RECYCLED_FACTOR,
    WASTE_DISPOSAL_FACTORS,
    EmissionFactor,
)

Strategy = Literal[
    "reduce", "reuse", "recycle", "substitute", "recover", "process_optimization"
]
CostTier = Literal["low", "medium", "high"]

# Fixed reduction percentage used by all `reduce` / `process_optimization`
# fallback candidates that have no natural factor-table swap to compute
# against (PRD §12 example figure).
DEFAULT_REDUCTION_PERCENTAGE = Decimal("8")


@dataclass(frozen=True)
class RecommendationCandidate:
    strategy: Strategy
    title: str
    description: str
    estimated_cost: CostTier
    feasibility: int
    """Fixed 0-100 feasibility weight, documented per-strategy below."""
    payback_months: int
    alt_factor: EmissionFactor | None = None
    reduction_percentage: Decimal | None = None


# --- Energy candidates, keyed by `EnergyConsumption.energy_type` ---

_RENEWABLE_SWAP_CANDIDATE = RecommendationCandidate(
    strategy="substitute",
    title="Switch {activity} consumption to renewable electricity",
    description=(
        "Replace {activity}-sourced energy with certified renewable "
        "electricity (market-based, zero-rated Scope 2 factor) to "
        "eliminate the associated grid emission factor."
    ),
    estimated_cost="medium",
    feasibility=60,
    payback_months=18,
)

_ENERGY_EFFICIENCY_CANDIDATE = RecommendationCandidate(
    strategy="process_optimization",
    title="Improve energy efficiency for {activity} use",
    description=(
        "Implement process-level efficiency measures (load scheduling, "
        "equipment upgrades, insulation) to cut {activity} consumption by "
        f"a documented {DEFAULT_REDUCTION_PERCENTAGE}% without changing "
        "energy source."
    ),
    estimated_cost="low",
    feasibility=80,
    payback_months=6,
    reduction_percentage=DEFAULT_REDUCTION_PERCENTAGE,
)

ENERGY_RULES: dict[str, list[RecommendationCandidate]] = {
    "electricity": [
        RecommendationCandidate(
            strategy=_RENEWABLE_SWAP_CANDIDATE.strategy,
            title=_RENEWABLE_SWAP_CANDIDATE.title,
            description=_RENEWABLE_SWAP_CANDIDATE.description,
            estimated_cost=_RENEWABLE_SWAP_CANDIDATE.estimated_cost,
            feasibility=_RENEWABLE_SWAP_CANDIDATE.feasibility,
            payback_months=_RENEWABLE_SWAP_CANDIDATE.payback_months,
            alt_factor=ENERGY_EMISSION_FACTORS["renewable_electricity"],
        ),
        _ENERGY_EFFICIENCY_CANDIDATE,
    ],
    "natural_gas": [
        RecommendationCandidate(
            strategy=_RENEWABLE_SWAP_CANDIDATE.strategy,
            title=_RENEWABLE_SWAP_CANDIDATE.title,
            description=_RENEWABLE_SWAP_CANDIDATE.description,
            estimated_cost=_RENEWABLE_SWAP_CANDIDATE.estimated_cost,
            feasibility=_RENEWABLE_SWAP_CANDIDATE.feasibility,
            payback_months=_RENEWABLE_SWAP_CANDIDATE.payback_months,
            alt_factor=ENERGY_EMISSION_FACTORS["renewable_electricity"],
        ),
        RecommendationCandidate(
            strategy="recover",
            title="Recover waste heat from {activity} combustion",
            description=(
                "Install heat-recovery equipment to capture and reuse waste "
                "heat from {activity} combustion, cutting net fuel demand by "
                f"a documented {DEFAULT_REDUCTION_PERCENTAGE}%."
            ),
            estimated_cost="high",
            feasibility=50,
            payback_months=30,
            reduction_percentage=DEFAULT_REDUCTION_PERCENTAGE,
        ),
        _ENERGY_EFFICIENCY_CANDIDATE,
    ],
    "diesel": [
        RecommendationCandidate(
            strategy=_RENEWABLE_SWAP_CANDIDATE.strategy,
            title=_RENEWABLE_SWAP_CANDIDATE.title,
            description=_RENEWABLE_SWAP_CANDIDATE.description,
            estimated_cost=_RENEWABLE_SWAP_CANDIDATE.estimated_cost,
            feasibility=_RENEWABLE_SWAP_CANDIDATE.feasibility,
            payback_months=_RENEWABLE_SWAP_CANDIDATE.payback_months,
            alt_factor=ENERGY_EMISSION_FACTORS["renewable_electricity"],
        ),
        _ENERGY_EFFICIENCY_CANDIDATE,
    ],
    "coal": [
        RecommendationCandidate(
            strategy=_RENEWABLE_SWAP_CANDIDATE.strategy,
            title=_RENEWABLE_SWAP_CANDIDATE.title,
            description=_RENEWABLE_SWAP_CANDIDATE.description,
            estimated_cost=_RENEWABLE_SWAP_CANDIDATE.estimated_cost,
            feasibility=_RENEWABLE_SWAP_CANDIDATE.feasibility,
            payback_months=_RENEWABLE_SWAP_CANDIDATE.payback_months,
            alt_factor=ENERGY_EMISSION_FACTORS["renewable_electricity"],
        ),
        _ENERGY_EFFICIENCY_CANDIDATE,
    ],
    "other": [
        RecommendationCandidate(
            strategy=_RENEWABLE_SWAP_CANDIDATE.strategy,
            title=_RENEWABLE_SWAP_CANDIDATE.title,
            description=_RENEWABLE_SWAP_CANDIDATE.description,
            estimated_cost=_RENEWABLE_SWAP_CANDIDATE.estimated_cost,
            feasibility=_RENEWABLE_SWAP_CANDIDATE.feasibility,
            payback_months=_RENEWABLE_SWAP_CANDIDATE.payback_months,
            alt_factor=ENERGY_EMISSION_FACTORS["renewable_electricity"],
        ),
        _ENERGY_EFFICIENCY_CANDIDATE,
    ],
    # Already zero-rated; no beneficial swap available, only efficiency.
    "renewable_electricity": [_ENERGY_EFFICIENCY_CANDIDATE],
}


# --- Materials candidates (category="materials") ---
# `material_name` is free text (see Step 05 spec), so materials candidates
# are keyed by category only, independent of the specific material name.

MATERIALS_CANDIDATES: list[RecommendationCandidate] = [
    RecommendationCandidate(
        strategy="substitute",
        title="Increase recycled content of {activity}",
        description=(
            "Substitute virgin {activity} input with recycled-content "
            "material to reduce the embodied emission factor per kg."
        ),
        estimated_cost="medium",
        feasibility=55,
        payback_months=12,
        alt_factor=MATERIAL_RECYCLED_FACTOR,
    ),
    RecommendationCandidate(
        strategy="process_optimization",
        title="Reduce {activity} material consumption",
        description=(
            "Apply lean-material process improvements (yield optimization, "
            "scrap reduction, design-for-material-efficiency) to cut "
            f"{{activity}} input by a documented {DEFAULT_REDUCTION_PERCENTAGE}%."
        ),
        estimated_cost="low",
        feasibility=75,
        payback_months=9,
        reduction_percentage=DEFAULT_REDUCTION_PERCENTAGE,
    ),
]


# --- Waste candidates, keyed by `Waste.disposal_method` ---

_WASTE_EFFICIENCY_CANDIDATE = RecommendationCandidate(
    strategy="process_optimization",
    title="Reduce {activity} waste generation",
    description=(
        "Implement source-reduction measures to cut the volume of "
        f"{{activity}} waste generated by a documented {DEFAULT_REDUCTION_PERCENTAGE}%."
    ),
    estimated_cost="low",
    feasibility=70,
    payback_months=6,
    reduction_percentage=DEFAULT_REDUCTION_PERCENTAGE,
)

WASTE_RULES: dict[str, list[RecommendationCandidate]] = {
    "landfilled": [
        RecommendationCandidate(
            strategy="recycle",
            title="Divert {activity} waste to recycling",
            description=(
                "Route currently landfilled waste through a recycling "
                "stream instead, replacing the landfill disposal factor "
                "with the lower recycled-waste factor."
            ),
            estimated_cost="low",
            feasibility=70,
            payback_months=8,
            alt_factor=WASTE_DISPOSAL_FACTORS["recycled"],
        ),
        RecommendationCandidate(
            strategy="reuse",
            title="Reuse {activity} waste on-site or with partners",
            description=(
                "Establish a reuse pathway for currently landfilled waste "
                "(on-site reuse or industrial-symbiosis partner), replacing "
                "the landfill disposal factor with the lower reused-waste "
                "factor."
            ),
            estimated_cost="medium",
            feasibility=50,
            payback_months=15,
            alt_factor=WASTE_DISPOSAL_FACTORS["reused"],
        ),
        _WASTE_EFFICIENCY_CANDIDATE,
    ],
    "other": [
        RecommendationCandidate(
            strategy="recycle",
            title="Divert {activity} waste to recycling",
            description=(
                "Route currently unspecified-disposal waste through a "
                "recycling stream instead, replacing the disposal factor "
                "with the lower recycled-waste factor."
            ),
            estimated_cost="low",
            feasibility=65,
            payback_months=9,
            alt_factor=WASTE_DISPOSAL_FACTORS["recycled"],
        ),
        RecommendationCandidate(
            strategy="reuse",
            title="Reuse {activity} waste on-site or with partners",
            description=(
                "Establish a reuse pathway for currently unspecified-"
                "disposal waste, replacing the disposal factor with the "
                "lower reused-waste factor."
            ),
            estimated_cost="medium",
            feasibility=45,
            payback_months=16,
            alt_factor=WASTE_DISPOSAL_FACTORS["reused"],
        ),
        _WASTE_EFFICIENCY_CANDIDATE,
    ],
    # Already low-impact disposal routes; only source reduction offers
    # further benefit.
    "recycled": [_WASTE_EFFICIENCY_CANDIDATE],
    "reused": [_WASTE_EFFICIENCY_CANDIDATE],
    "sold": [_WASTE_EFFICIENCY_CANDIDATE],
}


# Fallback for any `(category, activity)` combination not otherwise mapped
# (including unrecognized categories), so every hotspot always yields at
# least one recommendation.
FALLBACK_CANDIDATE = RecommendationCandidate(
    strategy="process_optimization",
    title="Optimize {activity} process efficiency",
    description=(
        "Apply general process-optimization measures to reduce the "
        f"emissions intensity of {{activity}} by a documented "
        f"{DEFAULT_REDUCTION_PERCENTAGE}%."
    ),
    estimated_cost="low",
    feasibility=60,
    payback_months=12,
    reduction_percentage=DEFAULT_REDUCTION_PERCENTAGE,
)


def get_candidates(category: str, activity: str) -> list[RecommendationCandidate]:
    """Return the fixed candidate list for a hotspot's `(category, activity)`.

    Always returns at least one candidate (the fallback), never an empty
    list.
    """

    if category == "energy":
        return ENERGY_RULES.get(activity, [FALLBACK_CANDIDATE])
    if category == "materials":
        return MATERIALS_CANDIDATES
    if category == "waste":
        return WASTE_RULES.get(activity, [FALLBACK_CANDIDATE])
    return [FALLBACK_CANDIDATE]
