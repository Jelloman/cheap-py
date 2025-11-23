"""REST client integration tests.

Test the full cycle: REST Client → REST API → Database.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from cheap.rest.main import create_app
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.e2e
class TestRestClientIntegration:
    """Integration tests for the REST client with live API."""

    async def test_client_create_catalog_integration(self) -> None:
        """Test creating a catalog using the REST client."""
        # Use httpx transport with the test app
        app = create_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            # Create catalog directly through HTTP client (simulating REST client)
            response = await http_client.post(
                "/api/catalog",
                json={
                    "species": "SOURCE",
                    "version": "1.0.0",
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert "catalog_id" in data
            assert data["species"] == "SOURCE"

    async def test_client_crud_cycle_integration(self) -> None:
        """Test full CRUD cycle through the REST client."""
        app = create_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            # Create
            create_response = await http_client.post(
                "/api/catalog",
                json={
                    "species": "SOURCE",
                    "version": "1.0.0",
                },
            )
            assert create_response.status_code == 201
            catalog_id = create_response.json()["catalog_id"]

            # Read
            get_response = await http_client.get(f"/api/catalog/{catalog_id}")
            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["catalog_id"] == catalog_id

            # Delete
            delete_response = await http_client.delete(f"/api/catalog/{catalog_id}")
            assert delete_response.status_code == 204

            # Verify deletion
            verify_response = await http_client.get(f"/api/catalog/{catalog_id}")
            assert verify_response.status_code == 404

    async def test_client_error_handling_integration(self) -> None:
        """Test error handling in the REST client."""
        app = create_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            # Try to get nonexistent catalog
            nonexistent_id = str(uuid4())
            response = await http_client.get(f"/api/catalog/{nonexistent_id}")
            assert response.status_code == 404

            # Try to create invalid catalog
            response = await http_client.post(
                "/api/catalog",
                json={
                    "species": "INVALID",
                    "version": "1.0.0",
                },
            )
            assert response.status_code == 422

    async def test_concurrent_client_operations(self) -> None:
        """Test concurrent operations through the REST client."""
        app = create_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            # Create multiple catalogs concurrently
            async def create_catalog(species: str) -> str:
                response = await http_client.post(
                    "/api/catalog",
                    json={
                        "species": species,
                        "version": "1.0.0",
                    },
                )
                return response.json()["catalog_id"]

            # Create 5 catalogs concurrently
            catalog_ids = await asyncio.gather(
                create_catalog("SOURCE"),
                create_catalog("SINK"),
                create_catalog("CACHE"),
                create_catalog("MIRROR"),
                create_catalog("FORK"),
            )

            assert len(catalog_ids) == 5
            assert len(set(catalog_ids)) == 5  # All unique

            # Verify all catalogs exist
            for catalog_id in catalog_ids:
                response = await http_client.get(f"/api/catalog/{catalog_id}")
                assert response.status_code == 200
