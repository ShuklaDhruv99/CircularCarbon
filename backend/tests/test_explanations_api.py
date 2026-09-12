"""API tests for the explanations generate route."""

from unittest.mock import patch

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


def test_generate_missing_factory_returns_404(client: TestClient) -> None:
    response = client.post("/api/explanations/generate/999999")
    assert response.status_code == 404


def test_generate_no_recommendations_returns_empty_list(client: TestClient) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")
    # Recommendations were never generated for this factory.

    response = client.post(f"/api/explanations/generate/{factory['id']}")
    assert response.status_code == 200
    assert response.json() == []


def test_generate_returns_one_explanation_per_recommendation_ordered(
    client: TestClient,
) -> None:
    factory = _create_factory(client)
    process = _create_process(client, factory["id"])
    _seed_process_data(client, process["id"])
    client.post(f"/api/emissions/calculate/{factory['id']}")
    generate_recs_response = client.post(
        f"/api/recommendations/generate/{factory['id']}"
    )
    recommendations = generate_recs_response.json()
    assert len(recommendations) > 0

    with patch(
        "app.services.explanation_service.generate_explanation"
    ) as mock_generate:
        from app.ai.gemini_client import GeminiUnavailableError

        mock_generate.side_effect = GeminiUnavailableError("no key configured")
        response = client.post(f"/api/explanations/generate/{factory['id']}")

    assert response.status_code == 200
    explanations = response.json()
    assert len(explanations) == len(recommendations)
    assert [e["recommendation_id"] for e in explanations] == [
        r["id"] for r in recommendations
    ]
    for explanation in explanations:
        assert explanation["source"] == "fallback"
        assert explanation["why"]
        assert explanation["what_to_do"]
        assert explanation["expected_benefit"]
        assert explanation["assumptions"]
