"""Natural-language explanation generation for circular recommendations.

For each currently-persisted `Recommendation` of a factory, builds a strict,
grounded prompt from that recommendation's own values and its parent
hotspot's values (Step 05/06 outputs), asks Gemini to narrate them, and
parses the four labeled sections back out. If Gemini is unavailable (no API
key configured, or the call fails/times out) or its response cannot be
parsed into the expected four sections, falls back to a deterministic
Python template built from the same verified values, so the feature degrades
gracefully rather than breaking the demo. Gemini is never asked to compute or
invent any numbers.
"""

import re
from decimal import Decimal

from sqlalchemy.orm import Session

from app.ai import prompts
from app.ai.gemini_client import GeminiUnavailableError, generate_explanation
from app.schemas.emission_result import HotspotRead
from app.schemas.explanation import ExplanationRead
from app.schemas.recommendation import RecommendationRead
from app.services import hotspot_service, recommendation_service

_SECTION_PATTERN = re.compile(
    r"why\s*:\s*(?P<why>.*?)\s*"
    r"what to do\s*:\s*(?P<what_to_do>.*?)\s*"
    r"expected benefit\s*:\s*(?P<expected_benefit>.*?)\s*"
    r"assumptions\s*:\s*(?P<assumptions>.*)",
    re.IGNORECASE | re.DOTALL,
)


def _render_optional(value: Decimal | None) -> str:
    return "not applicable" if value is None else str(value)


def _parse_gemini_response(text: str) -> dict[str, str]:
    match = _SECTION_PATTERN.search(text)
    if not match:
        raise ValueError("Gemini response did not contain the four required sections")

    sections = {key: value.strip() for key, value in match.groupdict().items()}
    if not all(sections.values()):
        raise ValueError("Gemini response had an empty required section")
    return sections


def _build_fallback(
    hotspot: HotspotRead, recommendation: RecommendationRead
) -> dict[str, str]:
    why = (
        f"{hotspot.activity} ({hotspot.category}) contributes {hotspot.co2e} kg CO2e, "
        f"{hotspot.percentage}% of total emissions, making it a priority hotspot."
    )
    what_to_do = (
        f"Implement the '{recommendation.title}' recommendation using a "
        f"{recommendation.strategy} strategy: {recommendation.description}"
    )
    expected_benefit = (
        f"Expected CO2 reduction of {recommendation.co2_reduction} kg CO2e, at an "
        f"estimated {recommendation.estimated_cost} cost tier, with a payback period "
        f"of {_render_optional(recommendation.payback_period)} months and a "
        f"recommendation score of {recommendation.score}."
    )
    assumptions = (
        "Figures are taken directly from the backend's verified deterministic "
        "calculation engine; no additional figures were assumed or invented."
    )
    return {
        "why": why,
        "what_to_do": what_to_do,
        "expected_benefit": expected_benefit,
        "assumptions": assumptions,
    }


def _build_explanation(
    hotspot: HotspotRead, recommendation: RecommendationRead
) -> ExplanationRead:
    prompt = prompts.build_prompt(hotspot, recommendation)

    try:
        response_text = generate_explanation(prompt)
        sections = _parse_gemini_response(response_text)
        source: str = "gemini"
    except (GeminiUnavailableError, ValueError):
        sections = _build_fallback(hotspot, recommendation)
        source = "fallback"

    return ExplanationRead(
        recommendation_id=recommendation.id,
        why=sections["why"],
        what_to_do=sections["what_to_do"],
        expected_benefit=sections["expected_benefit"],
        assumptions=sections["assumptions"],
        source=source,
    )


def generate_for_factory(db: Session, factory_id: int) -> list[ExplanationRead]:
    """Generate one explanation per currently-persisted recommendation.

    Reuses `recommendation_service.get_for_factory`'s `NotFoundError`
    semantics (propagated unchanged). Returns `[]` if the factory has zero
    recommendations. Order matches `get_for_factory` (score descending).
    """

    recommendations = recommendation_service.get_for_factory(db, factory_id)
    if not recommendations:
        return []

    hotspots = hotspot_service.get_hotspots(db, factory_id)
    hotspots_by_id = {hotspot.id: hotspot for hotspot in hotspots}

    explanations: list[ExplanationRead] = []
    for recommendation in recommendations:
        hotspot = hotspots_by_id[recommendation.hotspot_id]
        explanations.append(_build_explanation(hotspot, recommendation))

    return explanations
