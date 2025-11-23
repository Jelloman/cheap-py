"""Catalog-related Pydantic models."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from cheap.core.catalog_species import CatalogSpecies


class CreateCatalogRequest(BaseModel):
    """Request model for creating a new catalog."""

    species: CatalogSpecies
    version: str = Field(default="1.0.0", description="Catalog version")


class CreateCatalogResponse(BaseModel):
    """Response model for catalog creation."""

    catalog_id: UUID
    species: CatalogSpecies
    version: str
    message: str = "Catalog created successfully"


class CatalogResponse(BaseModel):
    """Response model for a single catalog."""

    catalog_id: UUID
    species: CatalogSpecies
    version: str


class CatalogListResponse(BaseModel):
    """Response model for paginated catalog list."""

    catalogs: list[CatalogResponse]
    page: int
    size: int
    total: int
