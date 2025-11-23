"""Cheap REST client implementation."""

from __future__ import annotations

import time
from typing import Any
from uuid import UUID

import httpx
from pydantic import TypeAdapter

from cheap.core.catalog import Catalog
from cheap.core.catalog_impl import CatalogImpl
from cheap.core.catalog_species import CatalogSpecies
from cheap.rest.client.config import CheapClientConfig
from cheap.rest.client.exceptions import (
    CheapRestBadRequestException,
    CheapRestClientException,
    CheapRestNotFoundException,
    CheapRestServerException,
)


class CheapClient:
    """Synchronous Cheap REST client.

    Provides type-safe access to the Cheap REST API with automatic retries
    and error handling.

    Example:
        ```python
        client = CheapClient(base_url="http://localhost:8000")
        catalog = client.create_catalog(species=CatalogSpecies.CHEAP)
        ```
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        retry_backoff_factor: float | None = None,
        config: CheapClientConfig | None = None,
    ) -> None:
        """Initialize the Cheap REST client.

        Args:
            base_url: Base URL of the Cheap REST API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff_factor: Exponential backoff factor for retries
            config: Configuration object (overrides individual params)
        """
        # Use config or create new one from parameters
        if config is None:
            config_kwargs: dict[str, Any] = {}
            if base_url is not None:
                config_kwargs["base_url"] = base_url
            if timeout is not None:
                config_kwargs["timeout"] = timeout
            if max_retries is not None:
                config_kwargs["max_retries"] = max_retries
            if retry_backoff_factor is not None:
                config_kwargs["retry_backoff_factor"] = retry_backoff_factor
            self.config = CheapClientConfig(**config_kwargs)
        else:
            self.config = config

        # Create HTTP client with connection pooling
        limits = httpx.Limits(
            max_connections=self.config.max_connections,
            max_keepalive_connections=self.config.max_keepalive_connections,
        )

        transport = httpx.HTTPTransport(retries=self.config.max_retries)

        self.client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            limits=limits,
            transport=transport,
        )

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self.client.close()

    def __enter__(self) -> CheapClient:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses.

        Args:
            response: HTTP response

        Raises:
            CheapRestNotFoundException: For 404 responses
            CheapRestBadRequestException: For 400 responses
            CheapRestServerException: For 5xx responses
            CheapRestClientException: For other errors
        """
        if response.status_code == 404:
            try:
                error_data = response.json()
                message = error_data.get("message", "Resource not found")
            except Exception:
                message = "Resource not found"
            raise CheapRestNotFoundException(message)

        if response.status_code == 400:
            try:
                error_data = response.json()
                message = error_data.get("message", "Bad request")
            except Exception:
                message = "Bad request"
            raise CheapRestBadRequestException(message)

        if 500 <= response.status_code < 600:
            try:
                error_data = response.json()
                message = error_data.get("message", f"Server error: {response.status_code}")
            except Exception:
                message = f"Server error: {response.status_code}"
            raise CheapRestServerException(message, status_code=response.status_code)

        # Other errors
        try:
            error_data = response.json()
            message = error_data.get("message", f"HTTP {response.status_code}")
        except Exception:
            message = f"HTTP {response.status_code}: {response.text}"
        raise CheapRestClientException(message, status_code=response.status_code)

    def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            url: URL path
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            CheapRestClientException: On error
        """
        last_exception: Exception | None = None

        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.client.request(method, url, **kwargs)

                if response.is_error:
                    self._handle_response_error(response)

                return response

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    # Exponential backoff
                    sleep_time = self.config.retry_backoff_factor * (2**attempt)
                    time.sleep(sleep_time)
                    continue
                # Last attempt failed
                break

            except (
                CheapRestNotFoundException,
                CheapRestBadRequestException,
                CheapRestServerException,
                CheapRestClientException,
            ):
                # Don't retry on client/server errors
                raise

        # All retries exhausted
        if last_exception:
            raise CheapRestClientException(
                f"Request failed after {self.config.max_retries + 1} attempts: {last_exception}"
            ) from last_exception

        raise CheapRestClientException(
            f"Request failed after {self.config.max_retries + 1} attempts"
        )

    def create_catalog(
        self,
        species: CatalogSpecies,
        version: str = "1.0.0",
    ) -> Catalog:
        """Create a new catalog.

        Args:
            species: Catalog species
            version: Catalog version

        Returns:
            Created catalog

        Raises:
            CheapRestBadRequestException: If request is invalid
            CheapRestClientException: On other errors
        """
        response = self._request_with_retry(
            "POST",
            "/catalogs",
            json={
                "species": species.value,
                "version": version,
            },
        )

        data = response.json()
        catalog_id = UUID(data["catalog_id"])

        return CatalogImpl(
            global_id=catalog_id,
            species=species,
            version=version,
        )

    def get_catalog(self, catalog_id: UUID) -> Catalog:
        """Get a catalog by ID.

        Args:
            catalog_id: Catalog ID

        Returns:
            Catalog

        Raises:
            CheapRestNotFoundException: If catalog not found
            CheapRestClientException: On other errors
        """
        response = self._request_with_retry("GET", f"/catalogs/{catalog_id}")

        data = response.json()

        return CatalogImpl(
            global_id=UUID(data["catalog_id"]),
            species=CatalogSpecies(data["species"]),
            version=data["version"],
        )

    def delete_catalog(self, catalog_id: UUID) -> None:
        """Delete a catalog.

        Args:
            catalog_id: Catalog ID

        Raises:
            CheapRestNotFoundException: If catalog not found
            CheapRestClientException: On other errors
        """
        self._request_with_retry("DELETE", f"/catalogs/{catalog_id}")

    def health_check(self) -> dict[str, str]:
        """Check API health status.

        Returns:
            Health status information

        Raises:
            CheapRestClientException: On error
        """
        response = self._request_with_retry("GET", "/health")
        return TypeAdapter(dict[str, str]).validate_python(response.json())


class AsyncCheapClient:
    """Asynchronous Cheap REST client.

    Provides type-safe async access to the Cheap REST API with automatic retries
    and error handling.

    Example:
        ```python
        async with AsyncCheapClient(base_url="http://localhost:8000") as client:
            catalog = await client.create_catalog(species=CatalogSpecies.CHEAP)
        ```
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        retry_backoff_factor: float | None = None,
        config: CheapClientConfig | None = None,
    ) -> None:
        """Initialize the async Cheap REST client.

        Args:
            base_url: Base URL of the Cheap REST API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff_factor: Exponential backoff factor for retries
            config: Configuration object (overrides individual params)
        """
        # Use config or create new one from parameters
        if config is None:
            config_kwargs: dict[str, Any] = {}
            if base_url is not None:
                config_kwargs["base_url"] = base_url
            if timeout is not None:
                config_kwargs["timeout"] = timeout
            if max_retries is not None:
                config_kwargs["max_retries"] = max_retries
            if retry_backoff_factor is not None:
                config_kwargs["retry_backoff_factor"] = retry_backoff_factor
            self.config = CheapClientConfig(**config_kwargs)
        else:
            self.config = config

        # Create HTTP client with connection pooling
        limits = httpx.Limits(
            max_connections=self.config.max_connections,
            max_keepalive_connections=self.config.max_keepalive_connections,
        )

        transport = httpx.AsyncHTTPTransport(retries=self.config.max_retries)

        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            limits=limits,
            transport=transport,
        )

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self.client.aclose()

    async def __aenter__(self) -> AsyncCheapClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses.

        Args:
            response: HTTP response

        Raises:
            CheapRestNotFoundException: For 404 responses
            CheapRestBadRequestException: For 400 responses
            CheapRestServerException: For 5xx responses
            CheapRestClientException: For other errors
        """
        if response.status_code == 404:
            try:
                error_data = response.json()
                message = error_data.get("message", "Resource not found")
            except Exception:
                message = "Resource not found"
            raise CheapRestNotFoundException(message)

        if response.status_code == 400:
            try:
                error_data = response.json()
                message = error_data.get("message", "Bad request")
            except Exception:
                message = "Bad request"
            raise CheapRestBadRequestException(message)

        if 500 <= response.status_code < 600:
            try:
                error_data = response.json()
                message = error_data.get("message", f"Server error: {response.status_code}")
            except Exception:
                message = f"Server error: {response.status_code}"
            raise CheapRestServerException(message, status_code=response.status_code)

        # Other errors
        try:
            error_data = response.json()
            message = error_data.get("message", f"HTTP {response.status_code}")
        except Exception:
            message = f"HTTP {response.status_code}: {response.text}"
        raise CheapRestClientException(message, status_code=response.status_code)

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make async HTTP request with retry logic.

        Args:
            method: HTTP method
            url: URL path
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            CheapRestClientException: On error
        """
        import asyncio

        last_exception: Exception | None = None

        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)

                if response.is_error:
                    self._handle_response_error(response)

                return response

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    # Exponential backoff
                    sleep_time = self.config.retry_backoff_factor * (2**attempt)
                    await asyncio.sleep(sleep_time)
                    continue
                # Last attempt failed
                break

            except (
                CheapRestNotFoundException,
                CheapRestBadRequestException,
                CheapRestServerException,
                CheapRestClientException,
            ):
                # Don't retry on client/server errors
                raise

        # All retries exhausted
        if last_exception:
            raise CheapRestClientException(
                f"Request failed after {self.config.max_retries + 1} attempts: {last_exception}"
            ) from last_exception

        raise CheapRestClientException(
            f"Request failed after {self.config.max_retries + 1} attempts"
        )

    async def create_catalog(
        self,
        species: CatalogSpecies,
        version: str = "1.0.0",
    ) -> Catalog:
        """Create a new catalog.

        Args:
            species: Catalog species
            version: Catalog version

        Returns:
            Created catalog

        Raises:
            CheapRestBadRequestException: If request is invalid
            CheapRestClientException: On other errors
        """
        response = await self._request_with_retry(
            "POST",
            "/catalogs",
            json={
                "species": species.value,
                "version": version,
            },
        )

        data = response.json()
        catalog_id = UUID(data["catalog_id"])

        return CatalogImpl(
            global_id=catalog_id,
            species=species,
            version=version,
        )

    async def get_catalog(self, catalog_id: UUID) -> Catalog:
        """Get a catalog by ID.

        Args:
            catalog_id: Catalog ID

        Returns:
            Catalog

        Raises:
            CheapRestNotFoundException: If catalog not found
            CheapRestClientException: On other errors
        """
        response = await self._request_with_retry("GET", f"/catalogs/{catalog_id}")

        data = response.json()

        return CatalogImpl(
            global_id=UUID(data["catalog_id"]),
            species=CatalogSpecies(data["species"]),
            version=data["version"],
        )

    async def delete_catalog(self, catalog_id: UUID) -> None:
        """Delete a catalog.

        Args:
            catalog_id: Catalog ID

        Raises:
            CheapRestNotFoundException: If catalog not found
            CheapRestClientException: On other errors
        """
        await self._request_with_retry("DELETE", f"/catalogs/{catalog_id}")

    async def health_check(self) -> dict[str, str]:
        """Check API health status.

        Returns:
            Health status information

        Raises:
            CheapRestClientException: On error
        """
        response = await self._request_with_retry("GET", "/health")
        return TypeAdapter(dict[str, str]).validate_python(response.json())
