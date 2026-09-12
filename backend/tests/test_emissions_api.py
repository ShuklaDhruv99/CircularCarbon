"""API tests for the emissions calculate/factory/hotspots routes."""

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
        "/api/energy",
        json={
            "process_id": process_id,
            "energy_type": "electricity",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )
    client.post(
        "/api/materials",
        json={
            "process_id": process_id,
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
            "recycled_percentage": "20",
        },
    )
    client.post(
        "/api/waste",
        json={
            "process_id": process_id,
            "waste_type": "slag",
            "quantity": "10",
            "unit": "kg",
            "disposal_method": "landfilled",
        },
    )


def test_calculate_emissions_returns_breakdown(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])

    response = client.post(f"/api/emissions/calculate/{factory['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["factory_id"] == factory["id"]
    assert len(body["results"]) == 3
    assert len(body["category_breakdown"]) == 3
    category_pct_sum = sum(float(c["percentage"]) for c in body["category_breakdown"])
    assert round(category_pct_sum, 2) == 100.00
    assert float(body["factory_total_co2e"]) > 0


def test_calculate_emissions_missing_factory_returns_404(client: TestClient) -> None:
    response = client.post("/api/emissions/calculate/999999")
    assert response.status_code == 404


def test_get_factory_emissions_before_calculation_returns_404(client: TestClient) -> None:
    factory = _create_factory(client)
    _create_process(client, factory["id"])

    response = client.get(f"/api/emissions/factory/{factory['id']}")

    assert response.status_code == 404


def test_get_factory_emissions_with_no_processes_returns_404(client: TestClient) -> None:
    factory = _create_factory(client)

    response = client.get(f"/api/emissions/factory/{factory['id']}")

    assert response.status_code == 404


def test_get_factory_emissions_missing_factory_returns_404(client: TestClient) -> None:
    response = client.get("/api/emissions/factory/999999")
    assert response.status_code == 404


def test_get_factory_emissions_after_calculation_returns_200(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")

    response = client.get(f"/api/emissions/factory/{factory['id']}")

    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 3


def test_get_factory_emissions_legitimately_zero_total_returns_200(
    client: TestClient,
) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    client.post(
        "/api/energy",
        json={
            "process_id": process["id"],
            "energy_type": "renewable_electricity",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )
    client.post(f"/api/emissions/calculate/{factory['id']}")

    response = client.get(f"/api/emissions/factory/{factory['id']}")

    assert response.status_code == 200
    body = response.json()
    assert float(body["factory_total_co2e"]) == 0.0


def test_recalculate_replaces_prior_results(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])

    client.post(f"/api/emissions/calculate/{factory['id']}")
    second_response = client.post(f"/api/emissions/calculate/{factory['id']}")

    assert second_response.status_code == 200
    assert len(second_response.json()["results"]) == 3


def test_get_hotspots_returns_ordered_results_with_flags(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")

    response = client.get(f"/api/emissions/hotspots/{factory['id']}")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    co2e_values = [float(row["co2e"]) for row in body]
    assert co2e_values == sorted(co2e_values, reverse=True)
    assert any(row["is_hotspot"] for row in body)


def test_get_hotspots_missing_factory_returns_404(client: TestClient) -> None:
    response = client.get("/api/emissions/hotspots/999999")
    assert response.status_code == 404


def test_get_hotspots_before_calculation_returns_404(client: TestClient) -> None:
    factory = _create_factory(client)
    _create_process(client, factory["id"])

    response = client.get(f"/api/emissions/hotspots/{factory['id']}")

    assert response.status_code == 404
