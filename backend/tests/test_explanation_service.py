"""Unit tests for the Gemini explanation generation/fallback pipeline."""

from decimal import Decimal
from unittest.mock import patch

from sqlalchemy.orm import Session

from app.ai.gemini_client import GeminiUnavailableError
from app.models import Material, Process, Factory
from app.services import (
    emission_calculation_service,
    explanation_service,
    recommendation_service,
)


def _make_factory_with_material_hotspot(db_session: Session) -> Factory:
    factory = Factory(name="Acme Steel", industry="steel", assessment_period="2025-Q1")
    db_session.add(factory)
    db_session.flush()
    process = Process(factory_id=factory.id, name="Smelting")
    db_session.add(process)
    db_session.flush()
    db_session.add(
        Material(
            process_id=process.id,
            material_name="Iron ore",
            quantity=Decimal("100"),
            unit="kg",
            recycled_percentage=Decimal("0"),
        )
    )
    db_session.commit()
    emission_calculation_service.calculate_for_factory(db_session, factory.id)
    recommendation_service.generate_for_factory(db_session, factory.id)
    return factory


def test_no_api_key_falls_back_with_no_network_call(db_session: Session) -> None:
    factory = _make_factory_with_material_hotspot(db_session)

    with patch("app.services.explanation_service.generate_explanation") as mock_call:
        mock_call.side_effect = GeminiUnavailableError("no key configured")
        explanations = explanation_service.generate_for_factory(db_session, factory.id)

    assert len(explanations) > 0
    for explanation in explanations:
        assert explanation.source == "fallback"
        assert explanation.why
        assert explanation.what_to_do
        assert explanation.expected_benefit
        assert explanation.assumptions
    mock_call.assert_called()


def test_well_formed_gemini_response_is_parsed(db_session: Session) -> None:
    factory = _make_factory_with_material_hotspot(db_session)

    mock_response = (
        "Why: This hotspot is significant.\n"
        "What to do: Swap to recycled material.\n"
        "Expected benefit: Reduces CO2e substantially.\n"
        "Assumptions: Figures are from the backend's verified calculation."
    )

    with patch(
        "app.services.explanation_service.generate_explanation",
        return_value=mock_response,
    ):
        explanations = explanation_service.generate_for_factory(db_session, factory.id)

    assert len(explanations) > 0
    for explanation in explanations:
        assert explanation.source == "gemini"
        assert explanation.why == "This hotspot is significant."
        assert explanation.what_to_do == "Swap to recycled material."
        assert explanation.expected_benefit == "Reduces CO2e substantially."
        assert (
            explanation.assumptions
            == "Figures are from the backend's verified calculation."
        )


def test_malformed_gemini_response_falls_back(db_session: Session) -> None:
    factory = _make_factory_with_material_hotspot(db_session)

    with patch(
        "app.services.explanation_service.generate_explanation",
        return_value="This is not a properly labeled response at all.",
    ):
        explanations = explanation_service.generate_for_factory(db_session, factory.id)

    assert len(explanations) > 0
    for explanation in explanations:
        assert explanation.source == "fallback"


def test_no_recommendations_returns_empty_list(db_session: Session) -> None:
    factory = Factory(name="Empty Factory", industry="steel", assessment_period="2025-Q1")
    db_session.add(factory)
    db_session.flush()
    process = Process(factory_id=factory.id, name="Idle")
    db_session.add(process)
    db_session.commit()
    db_session.add(
        Material(
            process_id=process.id,
            material_name="Renewable input",
            quantity=Decimal("0"),
            unit="kg",
            recycled_percentage=Decimal("100"),
        )
    )
    db_session.commit()
    emission_calculation_service.calculate_for_factory(db_session, factory.id)

    explanations = explanation_service.generate_for_factory(db_session, factory.id)
    assert explanations == []
