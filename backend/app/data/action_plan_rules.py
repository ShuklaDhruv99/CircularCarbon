"""Fixed phase-bucketing thresholds for the Prioritized Action Plan.

`Recommendation.estimated_cost` (a `CostTier`) and `Recommendation.payback_period`
(months) are combined via fixed, documented thresholds to deterministically
bucket each recommendation into one of three implementation horizons:

- "now"   (0-3 months):  low-effort, fast-payback interventions
- "next"  (3-12 months): moderate-effort interventions
- "later" (12+ months):  high-cost or long-payback interventions

Evaluated in this order (first match wins) -- see `action_plan_service.py`:

1. LATER  if `estimated_cost == "high"` OR `payback_period > LATER_PAYBACK_MONTHS_THRESHOLD`
2. NOW    if `estimated_cost == "low"` AND (`payback_period` is None OR `payback_period <= NOW_PAYBACK_MONTHS_THRESHOLD`)
3. NEXT   otherwise (e.g. `estimated_cost == "medium"`, or payback between the two thresholds)

This is an intentional "worst-of" bucketing: a high-cost or long-payback
recommendation always lands in the more conservative phase even if the other
dimension is favorable. These thresholds are a fixed MVP scale, not derived
from any external standard.
"""

NOW_PAYBACK_MONTHS_THRESHOLD = 6
"""Recommendations with a payback period at or below this many months (and
low estimated cost) are bucketed into the "now" phase."""

LATER_PAYBACK_MONTHS_THRESHOLD = 24
"""Recommendations with a payback period strictly above this many months are
always bucketed into the "later" phase, regardless of cost."""
