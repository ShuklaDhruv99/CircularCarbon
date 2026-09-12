"""API tests for factory CRUD routes."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import EnergyConsumption, Factory, Material, Process, Waste


def _create_factory(client: TestClient, name: str = "Acme Steel") -> dict:
    response = client.post(
        "/api/factories",
        json={"name": name, "industry": "Metal Manufacturing"},
    )
    assert response.status_code == 201
    return response.json()


def test_create_factory(client: TestClient) -> None:
    factory = _create_factory(client)

    assert factory["name"] == "Acme Steel"
    assert factory["industry"] == "Metal Manufacturing"
    assert factory["processes"] == []
    assert "id" in factory


def test_create_factory_invalid_industry_returns_422(client: TestClient) -> None:
    response = client.post(
        "/api/factories",
        json={"name": "Acme Steel", "industry": "Nonexistent Industry"},
    )

    assert response.status_code == 422


def test_list_factories(client: TestClient) -> None:
    _create_factory(client, "Factory One")
    _create_factory(client, "Factory Two")

    response = client.get("/api/factories")

    assert response.status_code == 200
    names = {f["name"] for f in response.json()}
    assert names == {"Factory One", "Factory Two"}


def test_get_factory_includes_nested_processes(client: TestClient) -> None:
    factory = _create_factory(client)
    process_response = client.post(
        "/api/processes", json={"name": "Smelting", "factory_id": factory["id"]}
    )
    assert process_response.status_code == 201

    response = client.get(f"/api/factories/{factory['id']}")

    assert response.status_code == 200
    body = response.json()
    assert len(body["processes"]) == 1
    assert body["processes"][0]["name"] == "Smelting"


def test_get_factory_missing_returns_404(client: TestClient) -> None:
    response = client.get("/api/factories/999999")

    assert response.status_code == 404


def test_update_factory(client: TestClient) -> None:
    factory = _create_factory(client)

    response = client.patch(
        f"/api/factories/{factory['id']}", json={"location": "Pune"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["location"] == "Pune"
    assert body["name"] == "Acme Steel"


def test_update_factory_missing_returns_404(client: TestClient) -> None:
    response = client.patch("/api/factories/999999", json={"location": "Pune"})

    assert response.status_code == 404


def test_delete_factory(client: TestClient) -> None:
    factory = _create_factory(client)

    response = client.delete(f"/api/factories/{factory['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/api/factories/{factory['id']}")
    assert get_response.status_code == 404


def test_delete_factory_cascades_to_children(
    client: TestClient, db_session: Session
) -> None:
    factory = _create_factory(client)
    process_response = client.post(
        "/api/processes", json={"name": "Smelting", "factory_id": factory["id"]}
    )
    process = process_response.json()

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

    delete_response = client.delete(f"/api/factories/{factory['id']}")
    assert delete_response.status_code == 204

    assert db_session.get(Factory, factory["id"]) is None
    assert db_session.get(Process, process["id"]) is None
    assert db_session.get(EnergyConsumption, energy_id) is None
    assert db_session.get(Material, material_id) is None
    assert db_session.get(Waste, waste_id) is None
