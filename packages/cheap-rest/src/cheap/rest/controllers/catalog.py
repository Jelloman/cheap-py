"""Catalog API endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from cheap.db.mariadb.dao import MariaDbDao
from cheap.db.postgres.dao import PostgresDao
from cheap.db.sqlite.dao import SqliteDao
from cheap.rest.database import get_dao
from cheap.rest.models.catalog import (
    CatalogResponse,
    CreateCatalogRequest,
    CreateCatalogResponse,
)
from cheap.rest.services.catalog import CatalogService

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])


@router.post(
    "",
    response_model=CreateCatalogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new catalog",
)
async def create_catalog(
    request: CreateCatalogRequest,
    dao: Annotated[SqliteDao | PostgresDao | MariaDbDao, Depends(get_dao)],
) -> CreateCatalogResponse:
    """Create a new catalog.

    Args:
        request: Catalog creation request
        dao: Database access object (injected)

    Returns:
        Catalog creation response with generated ID
    """
    service = CatalogService(dao)
    return await service.create_catalog(request)


@router.get(
    "/{catalog_id}",
    response_model=CatalogResponse,
    summary="Get catalog by ID",
)
async def get_catalog(
    catalog_id: UUID,
    dao: Annotated[SqliteDao | PostgresDao | MariaDbDao, Depends(get_dao)],
) -> CatalogResponse:
    """Get a catalog by its UUID.

    Args:
        catalog_id: UUID of the catalog
        dao: Database access object (injected)

    Returns:
        Catalog details
    """
    service = CatalogService(dao)
    return await service.get_catalog(catalog_id)


@router.delete(
    "/{catalog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete catalog",
)
async def delete_catalog(
    catalog_id: UUID,
    dao: Annotated[SqliteDao | PostgresDao | MariaDbDao, Depends(get_dao)],
) -> None:
    """Delete a catalog and all its data.

    Args:
        catalog_id: UUID of the catalog
        dao: Database access object (injected)
    """
    service = CatalogService(dao)
    await service.delete_catalog(catalog_id)
