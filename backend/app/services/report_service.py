"""PDF report generation for a factory's carbon assessment.

Orchestrates the existing deterministic services -- `factory_service`,
`emission_calculation_service`, `hotspot_service`, `recommendation_service`,
and `action_plan_service` -- in that fixed order, and renders their outputs
verbatim into a PDF via `reportlab`. Performs no new arithmetic: every number
in the report is taken directly from these upstream services. `NotFoundError`
raised by any of them propagates unchanged (not caught/re-raised here).

Computed on demand for every request; nothing is persisted or cached.
"""

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from app.schemas.action_plan import ActionPlanPhaseRead, ActionPlanRead
from app.schemas.emission_result import EmissionsBreakdownRead
from app.schemas.recommendation import RecommendationRead
from app.services import (
    action_plan_service,
    emission_calculation_service,
    factory_service,
    hotspot_service,
    recommendation_service,
)

COST_ESTIMATE_CAVEAT = (
    "Cost figures are fixed placeholder estimates for demonstration purposes "
    "only and do not represent real financial figures."
)

PHASE_LABELS: dict[str, str] = {
    "now": "Now",
    "next": "Next",
    "later": "Later",
}


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "Title": base["Title"],
        "Heading2": base["Heading2"],
        "Heading3": base["Heading3"],
        "Normal": base["Normal"],
    }


def _factory_info_flowables(factory, styles: dict[str, ParagraphStyle]) -> list:
    flowables = [Paragraph(f"Carbon Report: {factory.name}", styles["Title"])]
    flowables.append(Paragraph("Factory Information", styles["Heading2"]))
    flowables.append(Paragraph(f"Name: {factory.name}", styles["Normal"]))
    flowables.append(Paragraph(f"Industry: {factory.industry}", styles["Normal"]))
    flowables.append(
        Paragraph(f"Location: {factory.location or 'Not specified'}", styles["Normal"])
    )
    volume = factory.production_volume
    unit = factory.production_unit or ""
    volume_text = f"{volume} {unit}".strip() if volume is not None else "Not specified"
    flowables.append(Paragraph(f"Production volume: {volume_text}", styles["Normal"]))
    flowables.append(
        Paragraph(
            f"Assessment period: {factory.assessment_period or 'Not specified'}",
            styles["Normal"],
        )
    )
    flowables.append(Spacer(1, 0.5 * cm))
    return flowables


def _emissions_flowables(
    breakdown: EmissionsBreakdownRead, styles: dict[str, ParagraphStyle]
) -> list:
    flowables = [Paragraph("Current Total Emissions", styles["Heading2"])]
    flowables.append(
        Paragraph(
            f"Factory total CO2e: {breakdown.factory_total_co2e} kg CO2e",
            styles["Normal"],
        )
    )
    flowables.append(Spacer(1, 0.3 * cm))

    flowables.append(Paragraph("Emission Breakdown by Category", styles["Heading3"]))
    if breakdown.category_breakdown:
        for cat in breakdown.category_breakdown:
            flowables.append(
                Paragraph(
                    f"{cat.category}: {cat.co2e} kg CO2e ({cat.percentage}%)",
                    styles["Normal"],
                )
            )
    else:
        flowables.append(Paragraph("No category breakdown available.", styles["Normal"]))
    flowables.append(Spacer(1, 0.3 * cm))

    flowables.append(Paragraph("Emission Breakdown by Process", styles["Heading3"]))
    if breakdown.process_breakdown:
        for proc in breakdown.process_breakdown:
            flowables.append(
                Paragraph(
                    f"{proc.process_name}: {proc.co2e} kg CO2e ({proc.percentage}%)",
                    styles["Normal"],
                )
            )
    else:
        flowables.append(Paragraph("No process breakdown available.", styles["Normal"]))
    flowables.append(Spacer(1, 0.5 * cm))
    return flowables


def _hotspots_flowables(hotspots, styles: dict[str, ParagraphStyle]) -> list:
    flowables = [Paragraph("Top Hotspots", styles["Heading2"])]
    top = [h for h in hotspots if h.is_hotspot]
    if not top:
        flowables.append(Paragraph("No hotspots identified.", styles["Normal"]))
    for hotspot in top:
        flowables.append(
            Paragraph(
                f"{hotspot.category} / {hotspot.activity}: {hotspot.co2e} kg CO2e "
                f"({hotspot.percentage}%)",
                styles["Normal"],
            )
        )
    flowables.append(Spacer(1, 0.5 * cm))
    return flowables


def _recommendation_line(rec: RecommendationRead) -> str:
    payback = f"{rec.payback_period} months" if rec.payback_period is not None else "N/A"
    return (
        f"{rec.title} -- strategy: {rec.strategy}, estimated cost: {rec.estimated_cost} "
        f"({COST_ESTIMATE_CAVEAT}), CO2 reduction: {rec.co2_reduction} kg CO2e, "
        f"payback period: {payback}"
    )


def _recommendations_flowables(
    recommendations: list[RecommendationRead], styles: dict[str, ParagraphStyle]
) -> list:
    flowables = [Paragraph("Ranked Recommendations", styles["Heading2"])]
    if not recommendations:
        flowables.append(
            Paragraph("No recommendations generated yet.", styles["Normal"])
        )
    else:
        for rec in recommendations:
            flowables.append(Paragraph(_recommendation_line(rec), styles["Normal"]))
    flowables.append(Spacer(1, 0.5 * cm))
    return flowables


def _phase_flowables(
    phase: ActionPlanPhaseRead, styles: dict[str, ParagraphStyle]
) -> list:
    label = PHASE_LABELS[phase.phase]
    flowables = [Paragraph(label, styles["Heading3"])]
    if not phase.recommendations:
        flowables.append(
            Paragraph("No recommendations in this phase.", styles["Normal"])
        )
    else:
        for rec in phase.recommendations:
            flowables.append(Paragraph(_recommendation_line(rec), styles["Normal"]))
    flowables.append(
        Paragraph(
            f"Phase total CO2 reduction: {phase.total_co2_reduction} kg CO2e",
            styles["Normal"],
        )
    )
    flowables.append(
        Paragraph(
            f"Phase total implementation cost: {phase.total_implementation_cost} "
            f"({COST_ESTIMATE_CAVEAT})",
            styles["Normal"],
        )
    )
    flowables.append(Spacer(1, 0.3 * cm))
    return flowables


def _action_plan_flowables(
    plan: ActionPlanRead, styles: dict[str, ParagraphStyle]
) -> list:
    flowables = [Paragraph("Prioritized Action Plan", styles["Heading2"])]
    for phase in (plan.now, plan.next, plan.later):
        flowables.extend(_phase_flowables(phase, styles))
    return flowables


def generate_report_pdf(db: Session, factory_id: int) -> bytes:
    """Generate a PDF carbon report for a factory.

    Calls, in order: `factory_service.get`, `emission_calculation_service
    .get_breakdown`, `hotspot_service.get_hotspots`, `recommendation_service
    .get_for_factory`, `action_plan_service.get_action_plan`. Any
    `NotFoundError` raised by these calls propagates unchanged.
    """

    factory = factory_service.get(db, factory_id)
    breakdown = emission_calculation_service.get_breakdown(db, factory_id)
    hotspots = hotspot_service.get_hotspots(db, factory_id)
    recommendations = recommendation_service.get_for_factory(db, factory_id)
    plan = action_plan_service.get_action_plan(db, factory_id)

    styles = _styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    story: list = []
    story.extend(_factory_info_flowables(factory, styles))
    story.extend(_emissions_flowables(breakdown, styles))
    story.extend(_hotspots_flowables(hotspots, styles))
    story.extend(_recommendations_flowables(recommendations, styles))
    story.extend(_action_plan_flowables(plan, styles))

    doc.build(story)
    return buffer.getvalue()
