"""API tests for energy, material, and waste create/list/delete routes."""

from fastapi.testclient import TestClient


def _create_factory(client: TestClient, name: str = "Acme Steel") -> dict:
    response = client.post(
        "/api/factories",
        json={"name": name, "industry": "Metal Manufacturing"},
    )
    assert response.status_code == 201
    return response.json()


def _create_process(client: TestClient, factory_id: int, name: str = "Smelting") -> dict:
    response = client.post(
        "/api/processes", json={"name": name, "factory_id": factory_id}
    )
    assert response.status_code == 201
    return response.json()


def _setup_process(client: TestClient) -> dict:
    factory = _create_factory(client)
    return _create_process(client, factory["id"])


# --- Energy ---


def test_create_energy_entry(client: TestClient) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/energy",
        json={
            "process_id": process["id"],
            "energy_type": "electricity",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["process_id"] == process["id"]
    assert body["energy_type"] == "electricity"


def test_create_energy_entry_missing_process_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/energy",
        json={
            "process_id": 999999,
            "energy_type": "electricity",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )

    assert response.status_code == 404


def test_list_energy_filtered_by_process_id(client: TestClient) -> None:
    process_one = _setup_process(client)
    process_two = _create_process(client, process_one["factory_id"], "Process Two")

    client.post(
        "/api/energy",
        json={
            "process_id": process_one["id"],
            "energy_type": "electricity",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )
    client.post(
        "/api/energy",
        json={
            "process_id": process_two["id"],
            "energy_type": "diesel",
            "quantity": "50",
            "unit": "L",
            "period": "2025-Q1",
        },
    )

    response = client.get("/api/energy", params={"process_id": process_one["id"]})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["energy_type"] == "electricity"


def test_delete_energy_entry(client: TestClient) -> None:
    process = _setup_process(client)
    create_response = client.post(
        "/api/energy",
        json={
            "process_id": process["id"],
            "energy_type": "electricity",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )
    energy_id = create_response.json()["id"]

    response = client.delete(f"/api/energy/{energy_id}")

    assert response.status_code == 204


def test_create_energy_entry_non_positive_quantity_returns_422(client: TestClient) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/energy",
        json={
            "process_id": process["id"],
            "energy_type": "electricity",
            "quantity": "0",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )

    assert response.status_code == 422


def test_create_energy_entry_invalid_energy_type_returns_422(client: TestClient) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/energy",
        json={
            "process_id": process["id"],
            "energy_type": "nuclear",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )

    assert response.status_code == 422


# --- Materials ---


def test_create_material_entry(client: TestClient) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/materials",
        json={
            "process_id": process["id"],
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["process_id"] == process["id"]
    assert body["material_name"] == "Iron ore"


def test_create_material_entry_missing_process_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/materials",
        json={
            "process_id": 999999,
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
        },
    )

    assert response.status_code == 404


def test_list_materials_filtered_by_process_id(client: TestClient) -> None:
    process_one = _setup_process(client)
    process_two = _create_process(client, process_one["factory_id"], "Process Two")

    client.post(
        "/api/materials",
        json={
            "process_id": process_one["id"],
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
        },
    )
    client.post(
        "/api/materials",
        json={
            "process_id": process_two["id"],
            "material_name": "Cotton",
            "quantity": "20",
            "unit": "kg",
        },
    )

    response = client.get("/api/materials", params={"process_id": process_one["id"]})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["material_name"] == "Iron ore"


def test_delete_material_entry(client: TestClient) -> None:
    process = _setup_process(client)
    create_response = client.post(
        "/api/materials",
        json={
            "process_id": process["id"],
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
        },
    )
    material_id = create_response.json()["id"]

    response = client.delete(f"/api/materials/{material_id}")

    assert response.status_code == 204


def test_create_material_entry_non_positive_quantity_returns_422(client: TestClient) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/materials",
        json={
            "process_id": process["id"],
            "material_name": "Iron ore",
            "quantity": "-5",
            "unit": "kg",
        },
    )

    assert response.status_code == 422


def test_create_material_entry_recycled_percentage_below_zero_returns_422(
    client: TestClient,
) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/materials",
        json={
            "process_id": process["id"],
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
            "recycled_percentage": "-1",
        },
    )

    assert response.status_code == 422


def test_create_material_entry_recycled_percentage_above_100_returns_422(
    client: TestClient,
) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/materials",
        json={
            "process_id": process["id"],
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
            "recycled_percentage": "101",
        },
    )

    assert response.status_code == 422


# --- Waste ---


def test_create_waste_entry(client: TestClient) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/waste",
        json={
            "process_id": process["id"],
            "waste_type": "slag",
            "quantity": "10",
            "unit": "kg",
            "disposal_method": "landfilled",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["process_id"] == process["id"]
    assert body["waste_type"] == "slag"


def test_create_waste_entry_missing_process_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/waste",
        json={
            "process_id": 999999,
            "waste_type": "slag",
            "quantity": "10",
            "unit": "kg",
            "disposal_method": "landfilled",
        },
    )

    assert response.status_code == 404


def test_list_waste_filtered_by_process_id(client: TestClient) -> None:
    process_one = _setup_process(client)
    process_two = _create_process(client, process_one["factory_id"], "Process Two")

    client.post(
        "/api/waste",
        json={
            "process_id": process_one["id"],
            "waste_type": "slag",
            "quantity": "10",
            "unit": "kg",
            "disposal_method": "landfilled",
        },
    )
    client.post(
        "/api/waste",
        json={
            "process_id": process_two["id"],
            "waste_type": "offcuts",
            "quantity": "5",
            "unit": "kg",
            "disposal_method": "recycled",
        },
    )

    response = client.get("/api/waste", params={"process_id": process_one["id"]})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["waste_type"] == "slag"


def test_delete_waste_entry(client: TestClient) -> None:
    process = _setup_process(client)
    create_response = client.post(
        "/api/waste",
        json={
            "process_id": process["id"],
            "waste_type": "slag",
            "quantity": "10",
            "unit": "kg",
            "disposal_method": "landfilled",
        },
    )
    waste_id = create_response.json()["id"]

    response = client.delete(f"/api/waste/{waste_id}")

    assert response.status_code == 204


def test_create_waste_entry_non_positive_quantity_returns_422(client: TestClient) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/waste",
        json={
            "process_id": process["id"],
            "waste_type": "slag",
            "quantity": "0",
            "unit": "kg",
            "disposal_method": "landfilled",
        },
    )

    assert response.status_code == 422


def test_create_waste_entry_invalid_disposal_method_returns_422(client: TestClient) -> None:
    process = _setup_process(client)

    response = client.post(
        "/api/waste",
        json={
            "process_id": process["id"],
            "waste_type": "slag",
            "quantity": "10",
            "unit": "kg",
            "disposal_method": "incinerated",
        },
    )

    assert response.status_code == 422
