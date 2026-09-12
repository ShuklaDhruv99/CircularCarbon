"""Unit tests for the deterministic recommendation scoring/ranking pipeline.

Expected `co2_reduction` and `score` values below are hand-computed against
the fixed formula in the Step 06 spec ("Scoring determinism rules") using the
emission factors in `app/data/emission_factors.py` and the candidate
definitions in `app/data/recommendation_rules.py`.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import EnergyConsumption, Factory, Material, Process, Waste
from app.services import emission_calculation_service, recommendation_service


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


def test_material_hotspot_scores_match_hand_computed_values(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # 100 kg, 0% recycled -> effective factor 2.00 -> co2e = 200.00.
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

    recommendations = recommendation_service.generate_for_factory(db_session, factory.id)

    assert len(recommendations) == 2
    assert all(r.hotspot_category == "materials" for r in recommendations)
    assert all(r.hotspot_activity == "Iron ore" for r in recommendations)

    substitute = next(r for r in recommendations if r.strategy == "substitute")
    reduce_candidate = next(
        r for r in recommendations if r.strategy == "process_optimization"
    )

    # substitute: virgin (2.00) -> recycled (0.50) factor swap.
    # co2_reduction = 200.00 - (200.00/2.00)*0.50 = 200.00 - 50.00 = 150.00
    assert substitute.co2_reduction == Decimal("150.00")
    # Impact = min(150/200*100, 100) = 75.00
    # Final = 75*0.35 + 60(medium cost)*0.20 + 55(feasibility)*0.20
    #       + 70(substitute circularity)*0.15 + 70(12mo payback)*0.10
    #       = 26.25 + 12 + 11 + 10.5 + 7 = 66.75
    assert substitute.score == Decimal("66.75")

    # reduce fallback: 8% of 200.00 = 16.00
    assert reduce_candidate.co2_reduction == Decimal("16.00")
    # Impact = min(16/200*100, 100) = 8.00
    # Final = 8*0.35 + 100(low cost)*0.20 + 75(feasibility)*0.20
    #       + 50(process_optimization circularity)*0.15 + 70(9mo payback)*0.10
    #       = 2.8 + 20 + 15 + 7.5 + 7 = 52.30
    assert reduce_candidate.score == Decimal("52.30")

    # Ordered by score descending.
    assert recommendations[0].id == substitute.id
    assert recommendations[1].id == reduce_candidate.id


def test_waste_hotspot_scores_match_hand_computed_values(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # 100 kg landfilled -> co2e = 100 * 0.58 = 58.00
    db_session.add(
        Waste(
            process_id=process.id,
            waste_type="slag",
            quantity=Decimal("100"),
            unit="kg",
            disposal_method="landfilled",
        )
    )
    db_session.commit()
    emission_calculation_service.calculate_for_factory(db_session, factory.id)

    recommendations = recommendation_service.generate_for_factory(db_session, factory.id)

    assert len(recommendations) == 3
    recycle = next(r for r in recommendations if r.strategy == "recycle")
    reuse = next(r for r in recommendations if r.strategy == "reuse")
    reduce_candidate = next(
        r for r in recommendations if r.strategy == "process_optimization"
    )

    # recycle: landfilled (0.58) -> recycled (0.05).
    # co2_reduction = 58.00 - (58.00/0.58)*0.05 = 58.00 - 5.00 = 53.00
    assert recycle.co2_reduction == Decimal("53.00")
    # Impact = min(53/58*100, 100) = 91.38 (rounded)
    # Final = 91.38*0.35 + 100*0.20 + 70*0.20 + 100*0.15 + 70*0.10 = 87.98
    assert recycle.score == Decimal("87.98")

    # reuse: landfilled (0.58) -> reused (0.02).
    # co2_reduction = 58.00 - (58.00/0.58)*0.02 = 58.00 - 2.00 = 56.00
    assert reuse.co2_reduction == Decimal("56.00")
    assert reuse.score == Decimal("74.79")

    # process_optimization fallback: 8% of 58.00 = 4.64
    assert reduce_candidate.co2_reduction == Decimal("4.64")
    assert reduce_candidate.score == Decimal("54.30")

    # Ordered by score descending: recycle > reuse > process_optimization.
    assert [r.id for r in recommendations] == [recycle.id, reuse.id, reduce_candidate.id]


def test_energy_hotspot_scores_match_hand_computed_values(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # 1000 kWh electricity -> co2e = 1000 * 0.71 = 710.00
    db_session.add(
        EnergyConsumption(
            process_id=process.id,
            energy_type="electricity",
            quantity=Decimal("1000"),
            unit="kWh",
            period="2025-Q1",
        )
    )
    db_session.commit()
    emission_calculation_service.calculate_for_factory(db_session, factory.id)

    recommendations = recommendation_service.generate_for_factory(db_session, factory.id)

    assert len(recommendations) == 2
    substitute = next(r for r in recommendations if r.strategy == "substitute")
    reduce_candidate = next(
        r for r in recommendations if r.strategy == "process_optimization"
    )

    # substitute: grid electricity (0.71) -> renewable electricity (0.00).
    # co2_reduction = 710.00 - (710.00/0.71)*0.00 = 710.00
    assert substitute.co2_reduction == Decimal("710.00")
    # Impact = min(100, 100) = 100.00
    # Final = 100*0.35 + 60*0.20 + 60*0.20 + 70*0.15 + 40*0.10 = 73.50
    assert substitute.score == Decimal("73.50")

    # process_optimization fallback: 8% of 710.00 = 56.80
    assert reduce_candidate.co2_reduction == Decimal("56.80")
    assert reduce_candidate.score == Decimal("56.30")

    assert [r.id for r in recommendations] == [substitute.id, reduce_candidate.id]


def test_only_hotspot_rows_get_recommendations(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # Dominant energy contributor + tiny waste contributor (mirrors
    # test_hotspot_service's 80% threshold scenario).
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

    recommendations = recommendation_service.generate_for_factory(db_session, factory.id)

    assert recommendations
    assert all(r.hotspot_category == "energy" for r in recommendations)


def test_regenerate_replaces_prior_recommendations(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
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

    first = recommendation_service.generate_for_factory(db_session, factory.id)
    second = recommendation_service.generate_for_factory(db_session, factory.id)

    assert len(first) == len(second) == 2
    persisted = recommendation_service.get_for_factory(db_session, factory.id)
    assert len(persisted) == 2
    assert {r.id for r in persisted} == {r.id for r in second}
