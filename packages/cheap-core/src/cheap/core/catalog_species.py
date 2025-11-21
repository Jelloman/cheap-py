"""Catalog species enum for Cheap data system."""

from __future__ import annotations

from enum import Enum
from typing import Literal, TypeAlias


class CatalogSpecies(Enum):
    """
    Enumeration of catalog species (types/roles) in the Cheap system.

    Catalog species define the role and behavior of a catalog in the data
    pipeline, similar to how git repositories can serve different roles
    (origin, upstream, fork, etc.).
    """

    SOURCE = "SOURCE"
    """
    Source catalog: The original, authoritative source of data.
    Data flows from SOURCE catalogs to other catalog types.
    """

    SINK = "SINK"
    """
    Sink catalog: A destination for data writes.
    Data flows into SINK catalogs but typically doesn't flow out.
    """

    MIRROR = "MIRROR"
    """
    Mirror catalog: An exact read-only replica of another catalog.
    Stays synchronized with its source, typically for load distribution.
    """

    CACHE = "CACHE"
    """
    Cache catalog: A temporary, performance-optimized copy of data.
    May have incomplete data, optimized for read performance.
    """

    CLONE = "CLONE"
    """
    Clone catalog: A full, independent copy of another catalog.
    Can diverge from the original over time.
    """

    FORK = "FORK"
    """
    Fork catalog: A branched copy intended for independent development.
    Explicitly intended to diverge from the source.
    """

    def __str__(self) -> str:
        """Return the string representation of the catalog species."""
        return self.value

    def __repr__(self) -> str:
        """Return the detailed representation of the catalog species."""
        return f"CatalogSpecies.{self.name}"


# Type alias for catalog species literals
CatalogSpeciesLiteral: TypeAlias = Literal[
    "SOURCE",
    "SINK",
    "MIRROR",
    "CACHE",
    "CLONE",
    "FORK",
]
