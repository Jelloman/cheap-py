"""Catalog service layer."""

from __future__ import annotations

from uuid import UUID, uuid4

from cheap.core.catalog_impl import CatalogImpl
from cheap.db.mariadb.dao import MariaDbDao
from cheap.db.postgres.dao import PostgresDao
from cheap.db.sqlite.dao import SqliteDao
from cheap.rest.exceptions import ResourceNotFoundException
from cheap.rest.models.catalog import (
    CatalogListResponse,
    CatalogResponse,
    CreateCatalogRequest,
    CreateCatalogResponse,
)


class CatalogService:
    """Service for catalog operations."""

    def __init__(self, dao: SqliteDao | PostgresDao | MariaDbDao) -> None:
        """Initialize catalog service.

        Args:
            dao: Data access object for persistence
        """
        self.dao = dao

    async def create_catalog(self, request: CreateCatalogRequest) -> CreateCatalogResponse:
        """Create a new catalog.

        Args:
            request: Catalog creation request

        Returns:
            Catalog creation response with ID
        """
        catalog_id = uuid4()
        catalog = CatalogImpl(
            global_id=catalog_id,
            species=request.species,
            version=request.version,
        )

        await self.dao.save_catalog(catalog)

        return CreateCatalogResponse(
            catalog_id=catalog_id,
            species=request.species,
            version=request.version,
        )

    async def get_catalog(self, catalog_id: UUID) -> CatalogResponse:
        """Get a catalog by ID.

        Args:
            catalog_id: UUID of the catalog

        Returns:
            Catalog details

        Raises:
            ResourceNotFoundException: If catalog not found
        """
        try:
            catalog = await self.dao.load_catalog(catalog_id)
            return CatalogResponse(
                catalog_id=catalog.global_id,
                species=catalog.species,
                version=catalog.version,
            )
        except ValueError as e:
            raise ResourceNotFoundException(str(e)) from e

    async def delete_catalog(self, catalog_id: UUID) -> None:
        """Delete a catalog.

        Args:
            catalog_id: UUID of the catalog to delete

        Raises:
            ResourceNotFoundException: If catalog not found
        """
        try:
            await self.dao.delete_catalog(catalog_id)
        except ValueError as e:
            raise ResourceNotFoundException(str(e)) from e
