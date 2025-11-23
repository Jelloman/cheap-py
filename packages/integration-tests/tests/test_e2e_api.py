"""End-to-end REST API integration tests.

Test the full stack: REST API → Database → Response cycle.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from cheap.rest.main import create_app
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.e2e
class TestEndToEndAPIIntegration:
    """End-to-end tests for the REST API."""

    @pytest.fixture
    async def api_client(self) -> AsyncGenerator[AsyncClient, None]:
        """Create an async HTTP client for the API."""
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    async def test_create_and_get_catalog_e2e(self, api_client) -> None:
        """Test creating and retrieving a catalog through the API."""
        # Create a catalog
        create_response = await api_client.post(
            "/api/catalog",
            json={
                "species": "SOURCE",
                "version": "1.0.0",
            },
        )
        assert create_response.status_code == 201
        create_data = create_response.json()
        catalog_id = create_data["catalog_id"]

        # Retrieve the catalog
        get_response = await api_client.get(f"/api/catalog/{catalog_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()

        assert get_data["catalog_id"] == catalog_id
        assert get_data["species"] == "SOURCE"
        assert get_data["version"] == "1.0.0"

    async def test_delete_catalog_e2e(self, api_client) -> None:
        """Test deleting a catalog through the API."""
        # Create a catalog
        create_response = await api_client.post(
            "/api/catalog",
            json={
                "species": "SINK",
                "version": "1.0.0",
            },
        )
        assert create_response.status_code == 201
        catalog_id = create_response.json()["catalog_id"]

        # Delete the catalog
        delete_response = await api_client.delete(f"/api/catalog/{catalog_id}")
        assert delete_response.status_code == 204

        # Verify it's deleted
        get_response = await api_client.get(f"/api/catalog/{catalog_id}")
        assert get_response.status_code == 404

    async def test_get_nonexistent_catalog_e2e(self, api_client) -> None:
        """Test retrieving a nonexistent catalog."""
        nonexistent_id = str(uuid4())
        response = await api_client.get(f"/api/catalog/{nonexistent_id}")
        assert response.status_code == 404

    async def test_invalid_catalog_species_e2e(self, api_client) -> None:
        """Test validation for invalid catalog species."""
        response = await api_client.post(
            "/api/catalog",
            json={
                "species": "INVALID_SPECIES",
                "version": "1.0.0",
            },
        )
        assert response.status_code == 422  # Validation error

    async def test_multiple_catalogs_e2e(self, api_client) -> None:
        """Test creating multiple catalogs."""
        catalog_ids = []

        # Create multiple catalogs
        for species in ["SOURCE", "SINK", "CACHE"]:
            response = await api_client.post(
                "/api/catalog",
                json={
                    "species": species,
                    "version": "1.0.0",
                },
            )
            assert response.status_code == 201
            catalog_ids.append(response.json()["catalog_id"])

        # Verify each catalog
        for catalog_id in catalog_ids:
            response = await api_client.get(f"/api/catalog/{catalog_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["catalog_id"] == catalog_id
            assert data["species"] in ["SOURCE", "SINK", "CACHE"]

    async def test_health_check_e2e(self, api_client) -> None:
        """Test the health check endpoint."""
        response = await api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "version" in data
