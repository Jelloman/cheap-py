"""Tests for REST API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cheap.core.catalog_species import CatalogSpecies
from cheap.rest.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app.

    Returns:
        Test client instance
    """
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint returns success."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "version" in data


class TestCatalogEndpoints:
    """Tests for catalog API endpoints."""

    def test_create_catalog(self, client: TestClient) -> None:
        """Test creating a new catalog."""
        response = client.post(
            "/api/catalog",
            json={
                "species": CatalogSpecies.SOURCE.value,
                "version": "1.0.0",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "catalog_id" in data
        assert data["species"] == CatalogSpecies.SOURCE.value
        assert data["version"] == "1.0.0"
        assert data["message"] == "Catalog created successfully"

    def test_get_catalog(self, client: TestClient) -> None:
        """Test getting a catalog by ID."""
        # First create a catalog
        create_response = client.post(
            "/api/catalog",
            json={
                "species": CatalogSpecies.SOURCE.value,
                "version": "1.0.0",
            },
        )
        catalog_id = create_response.json()["catalog_id"]

        # Then retrieve it
        response = client.get(f"/api/catalog/{catalog_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["catalog_id"] == catalog_id
        assert data["species"] == CatalogSpecies.SOURCE.value
        assert data["version"] == "1.0.0"

    def test_get_nonexistent_catalog(self, client: TestClient) -> None:
        """Test getting a catalog that doesn't exist."""
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/catalog/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"] == "ResourceNotFoundException"

    def test_delete_catalog(self, client: TestClient) -> None:
        """Test deleting a catalog."""
        # First create a catalog
        create_response = client.post(
            "/api/catalog",
            json={
                "species": CatalogSpecies.SOURCE.value,
                "version": "1.0.0",
            },
        )
        catalog_id = create_response.json()["catalog_id"]

        # Then delete it
        response = client.delete(f"/api/catalog/{catalog_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/catalog/{catalog_id}")
        assert get_response.status_code == 404

    def test_validation_error(self, client: TestClient) -> None:
        """Test validation error handling."""
        response = client.post(
            "/api/catalog",
            json={
                "species": "INVALID_SPECIES",
                "version": "1.0.0",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"] == "ValidationError"
        assert "errors" in data
