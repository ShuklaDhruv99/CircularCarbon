"""Tests for the core SQLAlchemy models: relationships and cascade deletes."""

from sqlalchemy.orm import Session

from app.models import (
    EmissionResult,
    EnergyConsumption,
    Factory,
    Material,
    Process,
    Recommendation,
    Waste,
)


def test_relationships_and_cascade_delete(db_session: Session) -> None:
    factory = Factory(name="Acme Steel", industry="steel")
    db_session.add(factory)
    db_session.flush()

    process = Process(factory_id=factory.id, name="Smelting")
    db_session.add(process)
    db_session.flush()

    energy = EnergyConsumption(
        process_id=process.id,
        energy_type="electricity",
        quantity=1000,
        unit="kWh",
        period="2025-Q1",
    )
    material = Material(
        process_id=process.id,
        material_name="Iron ore",
        quantity=500,
        unit="kg",
    )
    waste = Waste(
        process_id=process.id,
        waste_type="slag",
        quantity=50,
        unit="kg",
        disposal_method="landfill",
    )
    emission_result = EmissionResult(
        process_id=process.id,
        category="energy",
        activity="electricity consumption",
        emission_factor=0.82,
        co2e=820,
        period="2025-Q1",
    )
    db_session.add_all([energy, material, waste, emission_result])
    db_session.flush()

    recommendation = Recommendation(
        hotspot_id=emission_result.id,
        title="Switch to renewable electricity",
        description="Move to a renewable energy supplier for the smelting process.",
        strategy="energy_efficiency",
        estimated_cost="medium",
        co2_reduction=200,
    )
    db_session.add(recommendation)
    db_session.commit()

    db_session.refresh(factory)
    db_session.refresh(process)
    db_session.refresh(emission_result)

    # Relationships resolve correctly.
    assert factory.processes == [process]
    assert process.factory is factory
    assert process.energy_consumption == [energy]
    assert process.materials == [material]
    assert process.waste == [waste]
    assert process.emission_results == [emission_result]
    assert emission_result.recommendations == [recommendation]
    assert recommendation.hotspot is emission_result

    factory_id = factory.id
    process_id = process.id
    emission_result_id = emission_result.id
    energy_id = energy.id
    material_id = material.id
    waste_id = waste.id
    recommendation_id = recommendation.id

    # Deleting the factory should cascade-delete all descendant rows.
    db_session.delete(factory)
    db_session.commit()

    assert db_session.get(Factory, factory_id) is None
    assert db_session.get(Process, process_id) is None
    assert db_session.get(EnergyConsumption, energy_id) is None
    assert db_session.get(Material, material_id) is None
    assert db_session.get(Waste, waste_id) is None
    assert db_session.get(EmissionResult, emission_result_id) is None
    assert db_session.get(Recommendation, recommendation_id) is None
