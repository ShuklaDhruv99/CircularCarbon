"""Fixed currency-cost lookup for What-If simulation cost aggregation.

`Recommendation.estimated_cost` stores a qualitative `CostTier` ("low",
"medium", "high") rather than a currency amount -- no per-unit energy or
material currency cost exists anywhere else in the schema. This table maps
each tier to a fixed placeholder currency value so that
`simulation_service` can aggregate a `total_implementation_cost` and a
cost-weighted `estimated_payback_months` for a selected set of
recommendations.

This is an explicitly fixed, documented placeholder scale for the 24-hour
hackathon MVP -- it is NOT a real cost estimate and must not be presented as
one. All values are in the same generic currency unit used elsewhere in the
demo data.
"""

from decimal import Decimal

COST_TIER_ESTIMATES: dict[str, Decimal] = {
    "low": Decimal("50000"),
    "medium": Decimal("200000"),
    "high": Decimal("500000"),
}
