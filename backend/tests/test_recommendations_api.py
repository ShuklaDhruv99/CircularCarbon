"""API tests for the recommendations generate/get routes."""

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
            "quantity": "1000",
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


def test_generate_then_get_returns_matching_ranked_data(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")

    generate_response = client.post(f"/api/recommendations/generate/{factory['id']}")
    assert generate_response.status_code == 200
    generated = generate_response.json()
    assert len(generated) > 0

    get_response = client.get(f"/api/recommendations/factory/{factory['id']}")
    assert get_response.status_code == 200
    fetched = get_response.json()

    assert [r["id"] for r in fetched] == [r["id"] for r in generated]
    scores = [float(r["score"]) for r in fetched]
    assert scores == sorted(scores, reverse=True)
    for row in fetched:
        assert "hotspot_category" in row
        assert "hotspot_activity" in row
        assert row["strategy"] in {
            "reduce",
            "reuse",
            "recycle",
            "substitute",
            "recover",
            "process_optimization",
        }
        assert row["estimated_cost"] in {"low", "medium", "high"}


def test_generate_missing_factory_returns_404(client: TestClient) -> None:
    response = client.post("/api/recommendations/generate/999999")
    assert response.status_code == 404


def test_generate_before_calculation_returns_404(client: TestClient) -> None:
    factory = _create_factory(client)
    _create_process(client, factory["id"])

    response = client.post(f"/api/recommendations/generate/{factory['id']}")
    assert response.status_code == 404


def test_get_missing_factory_returns_404(client: TestClient) -> None:
    response = client.get("/api/recommendations/factory/999999")
    assert response.status_code == 404


def test_get_before_calculation_returns_404(client: TestClient) -> None:
    factory = _create_factory(client)
    _create_process(client, factory["id"])

    response = client.get(f"/api/recommendations/factory/{factory['id']}")
    assert response.status_code == 404


def test_get_before_generation_but_after_calculation_returns_empty_list(
    client: TestClient,
) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")

    response = client.get(f"/api/recommendations/factory/{factory['id']}")

    assert response.status_code == 200
    assert response.json() == []


def test_zero_hotspots_returns_empty_list(client: TestClient) -> None:
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

    generate_response = client.post(f"/api/recommendations/generate/{factory['id']}")
    assert generate_response.status_code == 200
    assert generate_response.json() == []

    get_response = client.get(f"/api/recommendations/factory/{factory['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == []


def test_regenerate_replaces_prior_rows_no_duplicates(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")

    first = client.post(f"/api/recommendations/generate/{factory['id']}")
    second = client.post(f"/api/recommendations/generate/{factory['id']}")

    assert first.status_code == 200
    assert second.status_code == 200

    get_response = client.get(f"/api/recommendations/factory/{factory['id']}")
    assert get_response.status_code == 200
    persisted = get_response.json()

    second_ids = {r["id"] for r in second.json()}
    persisted_ids = {r["id"] for r in persisted}
    assert persisted_ids == second_ids
    assert len(persisted) == len(second.json())
