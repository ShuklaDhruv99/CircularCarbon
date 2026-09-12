"""Unit tests for `report_service.generate_report_pdf`."""

from decimal import Decimal
from io import BytesIO

import pytest
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.models import Factory, Material, Process
from app.services import emission_calculation_service, recommendation_service, report_service
from app.services.errors import NotFoundError


def _extract_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _make_factory(db_session: Session, name: str = "Acme Steel") -> Factory:
    factory = Factory(name=name, industry="steel", assessment_period="2025-Q1")
    db_session.add(factory)
    db_session.flush()
    return factory


def _make_process(db_session: Session, factory: Factory, name: str = "Smelting") -> Process:
    process = Process(factory_id=factory.id, name=name)
    db_session.add(process)
    db_session.flush()
    return process


def _seed_material(db_session: Session, process: Process) -> None:
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


def test_full_pipeline_produces_non_empty_pdf_with_expected_content(
    db_session: Session,
) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    _seed_material(db_session, process)

    breakdown = emission_calculation_service.calculate_for_factory(db_session, factory.id)
    recs = recommendation_service.generate_for_factory(db_session, factory.id)
    assert recs, "expected recommendations to be generated for the seeded hotspot"

    pdf_bytes = report_service.generate_report_pdf(db_session, factory.id)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")

    text = _extract_text(pdf_bytes)
    assert factory.name in text
    assert str(breakdown.factory_total_co2e) in text
    for hotspot_category in {h.category for h in breakdown.category_breakdown}:
        assert hotspot_category in text
    for rec in recs:
        assert rec.title in text
    for phase_label in ("Now", "Next", "Later"):
        assert phase_label in text


def test_generate_report_missing_factory_raises_not_found(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        report_service.generate_report_pdf(db_session, 999999)


def test_generate_report_factory_without_processes_raises_not_found(
    db_session: Session,
) -> None:
    factory = _make_factory(db_session)
    db_session.commit()

    with pytest.raises(NotFoundError):
        report_service.generate_report_pdf(db_session, factory.id)


def test_generate_report_uncalculated_factory_raises_not_found(
    db_session: Session,
) -> None:
    factory = _make_factory(db_session)
    _make_process(db_session, factory)
    db_session.commit()

    with pytest.raises(NotFoundError):
        report_service.generate_report_pdf(db_session, factory.id)


def test_empty_recommendations_still_produces_valid_pdf_with_notes(
    db_session: Session,
) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    _seed_material(db_session, process)
    emission_calculation_service.calculate_for_factory(db_session, factory.id)
    # No `generate_for_factory` call -> zero persisted recommendations.

    pdf_bytes = report_service.generate_report_pdf(db_session, factory.id)

    assert len(pdf_bytes) > 0
    text = _extract_text(pdf_bytes)
    assert "No recommendations generated yet." in text
    assert "No recommendations in this phase." in text
