"""API tests for process CRUD routes."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import EnergyConsumption, Material, Process, Waste


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


def test_create_process(client: TestClient) -> None:
    factory = _create_factory(client)

    process = _create_process(client, factory["id"])

    assert process["name"] == "Smelting"
    assert process["factory_id"] == factory["id"]
    assert process["energy_consumption"] == []
    assert process["materials"] == []
    assert process["waste"] == []


def test_create_process_missing_factory_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/processes", json={"name": "Smelting", "factory_id": 999999}
    )

    assert response.status_code == 404


def test_list_processes_unfiltered(client: TestClient) -> None:
    factory_one = _create_factory(client, "Factory One")
    factory_two = _create_factory(client, "Factory Two")
    _create_process(client, factory_one["id"], "Process A")
    _create_process(client, factory_two["id"], "Process B")

    response = client.get("/api/processes")

    assert response.status_code == 200
    names = {p["name"] for p in response.json()}
    assert names == {"Process A", "Process B"}


def test_list_processes_filtered_by_factory_id(client: TestClient) -> None:
    factory_one = _create_factory(client, "Factory One")
    factory_two = _create_factory(client, "Factory Two")
    _create_process(client, factory_one["id"], "Process A")
    _create_process(client, factory_two["id"], "Process B")

    response = client.get("/api/processes", params={"factory_id": factory_one["id"]})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Process A"


def test_get_process_includes_nested_activity_data(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])

    client.post(
        "/api/energy",
        json={
            "process_id": process["id"],
            "energy_type": "electricity",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )
    client.post(
        "/api/materials",
        json={
            "process_id": process["id"],
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
        },
    )
    client.post(
        "/api/waste",
        json={
            "process_id": process["id"],
            "waste_type": "slag",
            "quantity": "10",
            "unit": "kg",
            "disposal_method": "landfilled",
        },
    )

    response = client.get(f"/api/processes/{process['id']}")

    assert response.status_code == 200
    body = response.json()
    assert len(body["energy_consumption"]) == 1
    assert len(body["materials"]) == 1
    assert len(body["waste"]) == 1


def test_get_process_missing_returns_404(client: TestClient) -> None:
    response = client.get("/api/processes/999999")

    assert response.status_code == 404


def test_update_process(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])

    response = client.patch(
        f"/api/processes/{process['id']}", json={"process_type": "casting"}
    )

    assert response.status_code == 200
    assert response.json()["process_type"] == "casting"


def test_delete_process_cascades_to_children(
    client: TestClient, db_session: Session
) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])

    energy_response = client.post(
        "/api/energy",
        json={
            "process_id": process["id"],
            "energy_type": "electricity",
            "quantity": "100",
            "unit": "kWh",
            "period": "2025-Q1",
        },
    )
    material_response = client.post(
        "/api/materials",
        json={
            "process_id": process["id"],
            "material_name": "Iron ore",
            "quantity": "50",
            "unit": "kg",
        },
    )
    waste_response = client.post(
        "/api/waste",
        json={
            "process_id": process["id"],
            "waste_type": "slag",
            "quantity": "10",
            "unit": "kg",
            "disposal_method": "landfilled",
        },
    )

    energy_id = energy_response.json()["id"]
    material_id = material_response.json()["id"]
    waste_id = waste_response.json()["id"]

    response = client.delete(f"/api/processes/{process['id']}")
    assert response.status_code == 204

    assert db_session.get(Process, process["id"]) is None
    assert db_session.get(EnergyConsumption, energy_id) is None
    assert db_session.get(Material, material_id) is None
    assert db_session.get(Waste, waste_id) is None
