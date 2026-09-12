"""API tests for the What-If simulation route."""

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


def test_simulate_missing_factory_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/simulations/factory/999999", json={"recommendation_ids": []}
    )
    assert response.status_code == 404


def test_simulate_before_calculation_returns_404(client: TestClient) -> None:
    factory = _create_factory(client)
    _create_process(client, factory["id"])

    response = client.post(
        f"/api/simulations/factory/{factory['id']}", json={"recommendation_ids": []}
    )
    assert response.status_code == 404


def test_simulate_unknown_recommendation_id_returns_422(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")
    client.post(f"/api/recommendations/generate/{factory['id']}")

    response = client.post(
        f"/api/simulations/factory/{factory['id']}",
        json={"recommendation_ids": [999999]},
    )
    assert response.status_code == 422


def test_simulate_empty_selection_returns_zero_impact(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    calc_response = client.post(f"/api/emissions/calculate/{factory['id']}")
    baseline = calc_response.json()["factory_total_co2e"]
    client.post(f"/api/recommendations/generate/{factory['id']}")

    response = client.post(
        f"/api/simulations/factory/{factory['id']}", json={"recommendation_ids": []}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["factory_id"] == factory["id"]
    assert float(body["baseline_co2e"]) == float(baseline)
    assert float(body["projected_co2e"]) == float(baseline)
    assert body["co2_reduction"] == "0.00"
    assert body["reduction_percentage"] == "0.00"
    assert body["total_implementation_cost"] == "0.00"
    assert body["estimated_payback_months"] is None
    assert body["applied_recommendations"] == []


def test_simulate_valid_subset_returns_correct_payload_shape(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")
    generate_response = client.post(f"/api/recommendations/generate/{factory['id']}")
    recommendations = generate_response.json()
    selected_id = recommendations[0]["id"]

    response = client.post(
        f"/api/simulations/factory/{factory['id']}",
        json={"recommendation_ids": [selected_id]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["factory_id"] == factory["id"]
    assert set(body.keys()) == {
        "factory_id",
        "baseline_co2e",
        "projected_co2e",
        "co2_reduction",
        "reduction_percentage",
        "total_implementation_cost",
        "estimated_payback_months",
        "applied_recommendations",
    }
    assert len(body["applied_recommendations"]) == 1
    assert body["applied_recommendations"][0]["id"] == selected_id
    assert float(body["projected_co2e"]) == float(body["baseline_co2e"]) - float(
        body["co2_reduction"]
    )
