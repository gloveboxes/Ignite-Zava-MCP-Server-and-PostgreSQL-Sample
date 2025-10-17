"""
Tests for health check and root endpoints.
"""

from fastapi.testclient import TestClient


def test_health_check(test_client: TestClient):
    """Health endpoint returns status and database info."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "github-api"
    assert "database" in data
    assert data["database"] in ["connected", "disconnected"]


def test_root_endpoint(test_client: TestClient):
    """Root endpoint returns service info and available endpoints."""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "GitHub Popup Store API"
    assert data["status"] == "running"
    assert "endpoints" in data
    assert "/health" in data["endpoints"].values()
