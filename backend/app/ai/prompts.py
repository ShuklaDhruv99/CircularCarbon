"""Builds the strict, grounded explanation prompt sent to Gemini.

The prompt is built exclusively from verified values already computed by the
deterministic engine (Step 05/06) -- `HotspotRead` and `RecommendationRead`
fields -- so Gemini has nothing to invent: it only narrates numbers the
backend already produced.
"""

from app.schemas.emission_result import HotspotRead
from app.schemas.recommendation import RecommendationRead

SECTION_HEADERS = ("Why", "What to do", "Expected benefit", "Assumptions")


def _render_optional(value: object) -> str:
    return "not applicable" if value is None else str(value)


def build_prompt(hotspot: HotspotRead, recommendation: RecommendationRead) -> str:
    """Build the grounded prompt for one hotspot/recommendation pair.

    Only the listed hotspot and recommendation fields are interpolated;
    Gemini is explicitly instructed never to invent or alter any figures.
    """

    return f"""You are an assistant that explains an already-computed circular-economy
recommendation to a factory manager. All numbers below are final and verified
by a deterministic backend calculation engine. You must NOT invent, estimate,
alter, or recompute any emission factors, costs, CO2 figures, or scores. Only
use the numbers explicitly provided below.

Hotspot data:
- Category: {hotspot.category}
- Activity: {hotspot.activity}
- CO2e: {hotspot.co2e} kg CO2e
- Percentage of total emissions: {hotspot.percentage}%

Recommendation data:
- Title: {recommendation.title}
- Strategy: {recommendation.strategy}
- Description: {recommendation.description}
- Estimated cost tier: {recommendation.estimated_cost}
- Estimated CO2 reduction: {recommendation.co2_reduction} kg CO2e
- Payback period (months): {_render_optional(recommendation.payback_period)}
- Score: {recommendation.score}

Respond with exactly four labeled sections, in this order, using these exact
labels followed by a colon:

Why: <explain why this hotspot/recommendation pairing matters, referencing
only the numbers above>
What to do: <concrete, practical next steps for implementing the
recommendation>
Expected benefit: <state the expected CO2 reduction and any cost/payback
context using only the numbers above>
Assumptions: <state that the figures come from the backend's verified
calculation, and note the payback period is "not applicable" if so>

Do not add any other sections, headings, or numbers not present above.
"""
