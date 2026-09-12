"""Unit tests for the deterministic emission calculation pipeline."""

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.models import EnergyConsumption, Factory, Material, Process, Waste
from app.services import emission_calculation_service
from app.services.errors import NotFoundError


def _make_factory(db_session: Session, assessment_period: str | None = "2025-Q1") -> Factory:
    factory = Factory(
        name="Acme Steel",
        industry="steel",
        assessment_period=assessment_period,
    )
    db_session.add(factory)
    db_session.flush()
    return factory


def _make_process(db_session: Session, factory: Factory, name: str = "Smelting") -> Process:
    process = Process(factory_id=factory.id, name=name)
    db_session.add(process)
    db_session.flush()
    return process


def test_energy_co2e_matches_hand_computed_value(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    db_session.add(
        EnergyConsumption(
            process_id=process.id,
            energy_type="electricity",
            quantity=Decimal("100"),
            unit="kWh",
            period="2025-Q1",
        )
    )
    db_session.commit()

    breakdown = emission_calculation_service.calculate_for_factory(db_session, factory.id)

    assert len(breakdown.results) == 1
    result = breakdown.results[0]
    # 100 kWh * 0.71 kg CO2e/kWh = 71.00
    assert result.co2e == Decimal("71.00")
    assert result.emission_factor == Decimal("0.71")
    assert result.category == "energy"
    assert result.period == "2025-Q1"
    assert breakdown.factory_total_co2e == Decimal("71.00")


def test_material_co2e_uses_recycled_content_blend(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    db_session.add(
        Material(
            process_id=process.id,
            material_name="Iron ore",
            quantity=Decimal("100"),
            unit="kg",
            recycled_percentage=Decimal("50"),
        )
    )
    db_session.commit()

    breakdown = emission_calculation_service.calculate_for_factory(db_session, factory.id)

    assert len(breakdown.results) == 1
    result = breakdown.results[0]
    # effective_factor = 2.00 * 0.5 + 0.50 * 0.5 = 1.25; co2e = 100 * 1.25 = 125.00
    assert result.emission_factor == Decimal("1.25")
    assert result.co2e == Decimal("125.00")
    assert result.category == "materials"
    # Materials have no period column -> derived from factory.assessment_period.
    assert result.period == "2025-Q1"


def test_waste_co2e_uses_disposal_method_factor_only(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    db_session.add(
        Waste(
            process_id=process.id,
            waste_type="slag",
            quantity=Decimal("10"),
            unit="kg",
            disposal_method="landfilled",
            recycled_quantity=Decimal("9999"),  # must be ignored per spec
        )
    )
    db_session.commit()

    breakdown = emission_calculation_service.calculate_for_factory(db_session, factory.id)

    assert len(breakdown.results) == 1
    result = breakdown.results[0]
    # 10 kg * 0.58 kg CO2e/kg = 5.80
    assert result.co2e == Decimal("5.80")
    assert result.category == "waste"


def test_period_falls_back_to_unspecified_when_no_assessment_period(
    db_session: Session,
) -> None:
    factory = _make_factory(db_session, assessment_period=None)
    process = _make_process(db_session, factory)
    db_session.add(
        Waste(
            process_id=process.id,
            waste_type="slag",
            quantity=Decimal("10"),
            unit="kg",
            disposal_method="landfilled",
        )
    )
    db_session.commit()

    breakdown = emission_calculation_service.calculate_for_factory(db_session, factory.id)

    assert breakdown.results[0].period == "unspecified"


def test_percentage_contributions_sum_to_100(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    db_session.add_all(
        [
            EnergyConsumption(
                process_id=process.id,
                energy_type="electricity",
                quantity=Decimal("100"),
                unit="kWh",
                period="2025-Q1",
            ),
            Material(
                process_id=process.id,
                material_name="Iron ore",
                quantity=Decimal("33"),
                unit="kg",
                recycled_percentage=Decimal("0"),
            ),
            Waste(
                process_id=process.id,
                waste_type="slag",
                quantity=Decimal("7"),
                unit="kg",
                disposal_method="landfilled",
            ),
        ]
    )
    db_session.commit()

    breakdown = emission_calculation_service.calculate_for_factory(db_session, factory.id)

    category_total = sum(c.percentage for c in breakdown.category_breakdown)
    assert category_total == Decimal("100.00")

    process_total = sum(p.percentage for p in breakdown.process_breakdown)
    assert process_total == Decimal("100.00")


def test_recalculate_replaces_prior_results(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    db_session.add(
        EnergyConsumption(
            process_id=process.id,
            energy_type="electricity",
            quantity=Decimal("100"),
            unit="kWh",
            period="2025-Q1",
        )
    )
    db_session.commit()

    first = emission_calculation_service.calculate_for_factory(db_session, factory.id)
    assert len(first.results) == 1

    second = emission_calculation_service.calculate_for_factory(db_session, factory.id)
    assert len(second.results) == 1
    # Recalculating with the same input twice should not duplicate rows.
    assert second.factory_total_co2e == first.factory_total_co2e


def test_calculate_for_missing_factory_raises_not_found(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        emission_calculation_service.calculate_for_factory(db_session, 999999)


def test_get_breakdown_raises_not_found_when_no_processes(db_session: Session) -> None:
    factory = _make_factory(db_session)
    db_session.commit()

    with pytest.raises(NotFoundError):
        emission_calculation_service.get_breakdown(db_session, factory.id)


def test_get_breakdown_raises_not_found_when_not_yet_calculated(db_session: Session) -> None:
    factory = _make_factory(db_session)
    _make_process(db_session, factory)
    db_session.commit()

    with pytest.raises(NotFoundError):
        emission_calculation_service.get_breakdown(db_session, factory.id)


def test_get_breakdown_returns_zero_total_when_legitimately_zero(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    db_session.add(
        EnergyConsumption(
            process_id=process.id,
            energy_type="renewable_electricity",
            quantity=Decimal("100"),
            unit="kWh",
            period="2025-Q1",
        )
    )
    db_session.commit()

    emission_calculation_service.calculate_for_factory(db_session, factory.id)
    breakdown = emission_calculation_service.get_breakdown(db_session, factory.id)

    assert breakdown.factory_total_co2e == Decimal("0")
    assert all(c.percentage == Decimal("0.00") for c in breakdown.category_breakdown)
