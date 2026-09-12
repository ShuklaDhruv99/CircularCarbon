"""API tests for the Prioritized Action Plan route."""

from fastapi.testclient import TestClient


def _create_factory(client: TestClient, name: str = "Acme Steel") -> dict:
    response = client.post(
        "/api/factories",
        json={"name": name, "industry": "Metal Manufacturing", "assessment_period": "2025-Q1"},
    )
    assert response.status_code == 201
    return response.json()


def _create_process(client: TestClient, factory_id: int, name: str = "Smelting") -> dict:
    response = client.post(
        "/api/processes", json={"name": name, "factory_id": factory_id}
    )
    assert response.status_code == 201
    return response.json()


def _seed_process_data(client: TestClient, process_id: int) -> None:
    client.post(
        "/api/materials",
        json={
            "process_id": process_id,
            "material_name": "Iron ore",
            "quantity": "100",
            "unit": "kg",
            "recycled_percentage": "0",
        },
    )


def test_action_plan_missing_factory_returns_404(client: TestClient) -> None:
    response = client.get("/api/action-plan/factory/999999")
    assert response.status_code == 404


def test_action_plan_before_calculation_returns_404(client: TestClient) -> None:
    factory = _create_factory(client)
    _create_process(client, factory["id"])

    response = client.get(f"/api/action-plan/factory/{factory['id']}")
    assert response.status_code == 404


def test_action_plan_empty_when_zero_recommendations(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    calc_response = client.post(f"/api/emissions/calculate/{factory['id']}")
    assert calc_response.status_code == 200
    # No `generate` call -> zero persisted recommendations, but the factory
    # has been calculated so the plan is 200 with three empty phases.

    response = client.get(f"/api/action-plan/factory/{factory['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["factory_id"] == factory["id"]
    for phase_key in ("now", "next", "later"):
        phase = body[phase_key]
        assert phase["phase"] == phase_key
        assert phase["recommendations"] == []
        assert phase["total_co2_reduction"] == "0.00"
        assert phase["total_implementation_cost"] == "0.00"


def test_action_plan_populated_partitions_all_recommendations(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")
    generate_response = client.post(f"/api/recommendations/generate/{factory['id']}")
    assert generate_response.status_code == 200
    recommendations = generate_response.json()
    assert recommendations, "expected recommendations to be generated"

    response = client.get(f"/api/action-plan/factory/{factory['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["factory_id"] == factory["id"]

    all_ids: list[int] = []
    for phase_key in ("now", "next", "later"):
        phase = body[phase_key]
        assert phase["phase"] == phase_key
        all_ids.extend(r["id"] for r in phase["recommendations"])

    assert sorted(all_ids) == sorted(r["id"] for r in recommendations)
    assert len(all_ids) == len(set(all_ids))
