"""API tests for the PDF report export route."""

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


def test_report_missing_factory_returns_404(client: TestClient) -> None:
    response = client.get("/api/report/factory/999999")
    assert response.status_code == 404


def test_report_before_calculation_returns_404(client: TestClient) -> None:
    factory = _create_factory(client)
    _create_process(client, factory["id"])

    response = client.get(f"/api/report/factory/{factory['id']}")
    assert response.status_code == 404


def test_report_populated_factory_returns_pdf(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    calc_response = client.post(f"/api/emissions/calculate/{factory['id']}")
    assert calc_response.status_code == 200
    generate_response = client.post(f"/api/recommendations/generate/{factory['id']}")
    assert generate_response.status_code == 200

    response = client.get(f"/api/report/factory/{factory['id']}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    content_disposition = response.headers["content-disposition"]
    assert "attachment" in content_disposition
    assert "carbon-report.pdf" in content_disposition
    assert len(response.content) > 0
    assert response.content.startswith(b"%PDF")
