"""Tests for Cheap REST client."""

from __future__ import annotations

from uuid import uuid4

import httpx
import pytest
import respx
from cheap.core.catalog_species import CatalogSpecies

from cheap.rest.client import (
    AsyncCheapClient,
    CheapClient,
    CheapRestBadRequestException,
    CheapRestClientException,
    CheapRestNotFoundException,
    CheapRestServerException,
)


class TestCheapClientSync:
    """Test suite for synchronous CheapClient."""

    def test_create_catalog(self) -> None:
        """Test creating a catalog."""
        catalog_id = uuid4()

        with respx.mock:
            respx.post("http://localhost:8000/catalogs").mock(
                return_value=httpx.Response(
                    201,
                    json={
                        "catalog_id": str(catalog_id),
                        "species": "SOURCE",
                        "version": "1.0.0",
                        "message": "Catalog created successfully",
                    },
                )
            )

            with CheapClient(base_url="http://localhost:8000") as client:
                catalog = client.create_catalog(species=CatalogSpecies.SOURCE, version="1.0.0")

                assert catalog.global_id == catalog_id
                assert catalog.species == CatalogSpecies.SOURCE
                assert catalog.version == "1.0.0"

    def test_get_catalog(self) -> None:
        """Test getting a catalog."""
        catalog_id = uuid4()

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "catalog_id": str(catalog_id),
                        "species": "SOURCE",
                        "version": "1.0.0",
                    },
                )
            )

            with CheapClient(base_url="http://localhost:8000") as client:
                catalog = client.get_catalog(catalog_id)

                assert catalog.global_id == catalog_id
                assert catalog.species == CatalogSpecies.SOURCE
                assert catalog.version == "1.0.0"

    def test_get_catalog_not_found(self) -> None:
        """Test getting a nonexistent catalog."""
        catalog_id = uuid4()

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                return_value=httpx.Response(
                    404,
                    json={
                        "error": "ResourceNotFoundException",
                        "message": "Catalog not found",
                        "path": f"/catalogs/{catalog_id}",
                    },
                )
            )

            with CheapClient(base_url="http://localhost:8000") as client:
                with pytest.raises(CheapRestNotFoundException) as exc_info:
                    client.get_catalog(catalog_id)

                assert exc_info.value.status_code == 404
                assert "Catalog not found" in exc_info.value.message

    def test_delete_catalog(self) -> None:
        """Test deleting a catalog."""
        catalog_id = uuid4()

        with respx.mock:
            respx.delete(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                return_value=httpx.Response(204)
            )

            with CheapClient(base_url="http://localhost:8000") as client:
                client.delete_catalog(catalog_id)

    def test_health_check(self) -> None:
        """Test health check endpoint."""
        with respx.mock:
            respx.get("http://localhost:8000/health").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "status": "healthy",
                        "database": "sqlite",
                        "version": "0.1.0",
                    },
                )
            )

            with CheapClient(base_url="http://localhost:8000") as client:
                health = client.health_check()

                assert health["status"] == "healthy"
                assert health["database"] == "sqlite"

    def test_bad_request_error(self) -> None:
        """Test bad request error handling."""
        with respx.mock:
            respx.post("http://localhost:8000/catalogs").mock(
                return_value=httpx.Response(
                    400,
                    json={
                        "error": "ValidationError",
                        "message": "Invalid catalog species",
                    },
                )
            )

            with CheapClient(base_url="http://localhost:8000") as client:
                with pytest.raises(CheapRestBadRequestException) as exc_info:
                    client.create_catalog(species=CatalogSpecies.SOURCE)

                assert exc_info.value.status_code == 400
                assert "Invalid catalog species" in exc_info.value.message

    def test_server_error(self) -> None:
        """Test server error handling."""
        catalog_id = uuid4()

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                return_value=httpx.Response(
                    500,
                    json={
                        "error": "InternalServerError",
                        "message": "Database connection failed",
                    },
                )
            )

            with CheapClient(base_url="http://localhost:8000") as client:
                with pytest.raises(CheapRestServerException) as exc_info:
                    client.get_catalog(catalog_id)

                assert exc_info.value.status_code == 500
                assert "Database connection failed" in exc_info.value.message

    def test_retry_on_network_error(self) -> None:
        """Test retry logic on network errors."""
        catalog_id = uuid4()
        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.NetworkError("Network error")
            return httpx.Response(
                200,
                json={
                    "catalog_id": str(catalog_id),
                    "species": "SOURCE",
                    "version": "1.0.0",
                },
            )

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(side_effect=side_effect)

            with CheapClient(
                base_url="http://localhost:8000", max_retries=3, retry_backoff_factor=0.01
            ) as client:
                catalog = client.get_catalog(catalog_id)

                assert catalog.global_id == catalog_id
                assert call_count == 3  # 2 retries + 1 success

    def test_retry_exhausted(self) -> None:
        """Test retry exhaustion."""
        catalog_id = uuid4()

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                side_effect=httpx.NetworkError("Network error")
            )

            with CheapClient(
                base_url="http://localhost:8000", max_retries=2, retry_backoff_factor=0.01
            ) as client:
                with pytest.raises(CheapRestClientException) as exc_info:
                    client.get_catalog(catalog_id)

                assert "failed after 3 attempts" in exc_info.value.message


class TestCheapClientAsync:
    """Test suite for asynchronous AsyncCheapClient."""

    async def test_create_catalog(self) -> None:
        """Test creating a catalog."""
        catalog_id = uuid4()

        with respx.mock:
            respx.post("http://localhost:8000/catalogs").mock(
                return_value=httpx.Response(
                    201,
                    json={
                        "catalog_id": str(catalog_id),
                        "species": "SOURCE",
                        "version": "1.0.0",
                        "message": "Catalog created successfully",
                    },
                )
            )

            async with AsyncCheapClient(base_url="http://localhost:8000") as client:
                catalog = await client.create_catalog(
                    species=CatalogSpecies.SOURCE, version="1.0.0"
                )

                assert catalog.global_id == catalog_id
                assert catalog.species == CatalogSpecies.SOURCE
                assert catalog.version == "1.0.0"

    async def test_get_catalog(self) -> None:
        """Test getting a catalog."""
        catalog_id = uuid4()

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "catalog_id": str(catalog_id),
                        "species": "SOURCE",
                        "version": "1.0.0",
                    },
                )
            )

            async with AsyncCheapClient(base_url="http://localhost:8000") as client:
                catalog = await client.get_catalog(catalog_id)

                assert catalog.global_id == catalog_id
                assert catalog.species == CatalogSpecies.SOURCE
                assert catalog.version == "1.0.0"

    async def test_get_catalog_not_found(self) -> None:
        """Test getting a nonexistent catalog."""
        catalog_id = uuid4()

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                return_value=httpx.Response(
                    404,
                    json={
                        "error": "ResourceNotFoundException",
                        "message": "Catalog not found",
                        "path": f"/catalogs/{catalog_id}",
                    },
                )
            )

            async with AsyncCheapClient(base_url="http://localhost:8000") as client:
                with pytest.raises(CheapRestNotFoundException) as exc_info:
                    await client.get_catalog(catalog_id)

                assert exc_info.value.status_code == 404
                assert "Catalog not found" in exc_info.value.message

    async def test_delete_catalog(self) -> None:
        """Test deleting a catalog."""
        catalog_id = uuid4()

        with respx.mock:
            respx.delete(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                return_value=httpx.Response(204)
            )

            async with AsyncCheapClient(base_url="http://localhost:8000") as client:
                await client.delete_catalog(catalog_id)

    async def test_health_check(self) -> None:
        """Test health check endpoint."""
        with respx.mock:
            respx.get("http://localhost:8000/health").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "status": "healthy",
                        "database": "sqlite",
                        "version": "0.1.0",
                    },
                )
            )

            async with AsyncCheapClient(base_url="http://localhost:8000") as client:
                health = await client.health_check()

                assert health["status"] == "healthy"
                assert health["database"] == "sqlite"

    async def test_retry_on_network_error(self) -> None:
        """Test retry logic on network errors."""
        catalog_id = uuid4()
        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.NetworkError("Network error")
            return httpx.Response(
                200,
                json={
                    "catalog_id": str(catalog_id),
                    "species": "SOURCE",
                    "version": "1.0.0",
                },
            )

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(side_effect=side_effect)

            async with AsyncCheapClient(
                base_url="http://localhost:8000", max_retries=3, retry_backoff_factor=0.01
            ) as client:
                catalog = await client.get_catalog(catalog_id)

                assert catalog.global_id == catalog_id
                assert call_count == 3  # 2 retries + 1 success

    async def test_retry_exhausted(self) -> None:
        """Test retry exhaustion."""
        catalog_id = uuid4()

        with respx.mock:
            respx.get(f"http://localhost:8000/catalogs/{catalog_id}").mock(
                side_effect=httpx.NetworkError("Network error")
            )

            async with AsyncCheapClient(
                base_url="http://localhost:8000", max_retries=2, retry_backoff_factor=0.01
            ) as client:
                with pytest.raises(CheapRestClientException) as exc_info:
                    await client.get_catalog(catalog_id)

                assert "failed after 3 attempts" in exc_info.value.message
