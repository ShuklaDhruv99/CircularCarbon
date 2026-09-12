"""Unit tests for hotspot ranking/threshold logic."""

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.models import EnergyConsumption, Factory, Material, Process, Waste
from app.services import emission_calculation_service, hotspot_service
from app.services.errors import NotFoundError


def _make_factory(db_session: Session) -> Factory:
    factory = Factory(name="Acme Steel", industry="steel", assessment_period="2025-Q1")
    db_session.add(factory)
    db_session.flush()
    return factory


def _make_process(db_session: Session, factory: Factory, name: str = "Smelting") -> Process:
    process = Process(factory_id=factory.id, name=name)
    db_session.add(process)
    db_session.flush()
    return process


def test_hotspots_ordered_by_co2e_descending_with_80pct_threshold(
    db_session: Session,
) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # Energy: 1000 kWh * 0.71 = 710.00 (dominant contributor)
    # Waste: 10 kg landfilled * 0.58 = 5.80 (tiny contributor)
    db_session.add_all(
        [
            EnergyConsumption(
                process_id=process.id,
                energy_type="electricity",
                quantity=Decimal("1000"),
                unit="kWh",
                period="2025-Q1",
            ),
            Waste(
                process_id=process.id,
                waste_type="slag",
                quantity=Decimal("10"),
                unit="kg",
                disposal_method="landfilled",
            ),
        ]
    )
    db_session.commit()
    emission_calculation_service.calculate_for_factory(db_session, factory.id)

    hotspots = hotspot_service.get_hotspots(db_session, factory.id)

    assert len(hotspots) == 2
    # Ordered CO2e descending.
    assert hotspots[0].co2e > hotspots[1].co2e
    assert hotspots[0].category == "energy"
    # The dominant contributor alone crosses 80% -> flagged; the small
    # remainder does not, since cumulative is already >= 80% before it.
    assert hotspots[0].is_hotspot is True
    assert hotspots[1].is_hotspot is False


def test_first_row_crossing_80pct_is_still_included(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # Two materials of equal weight (50/50 split); the first one crosses 80%
    # only when combined with... actually equal split means each is 50%, so
    # cumulative after first row is 50% (<80), it's a hotspot; after second
    # row cumulative reaches 100% but the second row's own contribution
    # pushes it there while previous cumulative (50%) was < 80 -> also a hotspot.
    db_session.add_all(
        [
            Material(
                process_id=process.id,
                material_name="Iron ore",
                quantity=Decimal("100"),
                unit="kg",
                recycled_percentage=Decimal("0"),
            ),
            Material(
                process_id=process.id,
                material_name="Copper",
                quantity=Decimal("100"),
                unit="kg",
                recycled_percentage=Decimal("0"),
            ),
        ]
    )
    db_session.commit()
    emission_calculation_service.calculate_for_factory(db_session, factory.id)

    hotspots = hotspot_service.get_hotspots(db_session, factory.id)

    assert len(hotspots) == 2
    assert all(h.is_hotspot for h in hotspots)


def test_no_hotspots_when_factory_total_is_zero(db_session: Session) -> None:
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

    hotspots = hotspot_service.get_hotspots(db_session, factory.id)

    assert len(hotspots) == 1
    assert hotspots[0].is_hotspot is False


def test_hotspots_raises_not_found_when_no_processes(db_session: Session) -> None:
    factory = _make_factory(db_session)
    db_session.commit()

    with pytest.raises(NotFoundError):
        hotspot_service.get_hotspots(db_session, factory.id)


def test_hotspots_raises_not_found_when_not_yet_calculated(db_session: Session) -> None:
    factory = _make_factory(db_session)
    _make_process(db_session, factory)
    db_session.commit()

    with pytest.raises(NotFoundError):
        hotspot_service.get_hotspots(db_session, factory.id)


def test_hotspots_raises_not_found_for_missing_factory(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        hotspot_service.get_hotspots(db_session, 999999)
