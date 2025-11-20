"""Catalog species enum for Cheap data system."""

from __future__ import annotations

from enum import Enum
from typing import Final, Literal, TypeAlias


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

    @property
    def is_read_only(self) -> bool:
        """
        Check if this catalog species is typically read-only.

        Returns:
            True if catalogs of this species are typically read-only.
        """
        return self in {CatalogSpecies.MIRROR, CatalogSpecies.CACHE}

    @property
    def is_writable(self) -> bool:
        """
        Check if this catalog species typically accepts writes.

        Returns:
            True if catalogs of this species typically accept writes.
        """
        return self in {
            CatalogSpecies.SOURCE,
            CatalogSpecies.SINK,
            CatalogSpecies.CLONE,
            CatalogSpecies.FORK,
        }

    @property
    def is_authoritative(self) -> bool:
        """
        Check if this catalog species is an authoritative data source.

        Returns:
            True if catalogs of this species are authoritative sources.
        """
        return self == CatalogSpecies.SOURCE

    @property
    def is_temporary(self) -> bool:
        """
        Check if this catalog species represents temporary data storage.

        Returns:
            True if catalogs of this species are intended for temporary storage.
        """
        return self == CatalogSpecies.CACHE

    @property
    def is_replica(self) -> bool:
        """
        Check if this catalog species is a replica of another catalog.

        Returns:
            True if catalogs of this species are replicas.
        """
        return self in {CatalogSpecies.MIRROR, CatalogSpecies.CACHE, CatalogSpecies.CLONE}

    @property
    def can_diverge(self) -> bool:
        """
        Check if this catalog species can diverge from its source.

        Returns:
            True if catalogs of this species can have different data than their source.
        """
        return self in {CatalogSpecies.CLONE, CatalogSpecies.FORK, CatalogSpecies.CACHE}

    def get_description(self) -> str:
        """
        Get a human-readable description of this catalog species.

        Returns:
            A description of what this catalog species represents.
        """
        descriptions: Final[dict[CatalogSpecies, str]] = {
            CatalogSpecies.SOURCE: (
                "Original authoritative source of data, primary data producer"
            ),
            CatalogSpecies.SINK: (
                "Destination for data writes, typically write-only or write-mostly"
            ),
            CatalogSpecies.MIRROR: (
                "Exact read-only replica, stays synchronized with source"
            ),
            CatalogSpecies.CACHE: (
                "Temporary performance-optimized copy, may have incomplete data"
            ),
            CatalogSpecies.CLONE: (
                "Full independent copy that can diverge from the original"
            ),
            CatalogSpecies.FORK: (
                "Branched copy explicitly intended for independent development"
            ),
        }
        return descriptions[self]

    def get_typical_use_case(self) -> str:
        """
        Get a typical use case for this catalog species.

        Returns:
            A description of when to use this catalog species.
        """
        use_cases: Final[dict[CatalogSpecies, str]] = {
            CatalogSpecies.SOURCE: "Primary database or master data source",
            CatalogSpecies.SINK: "Analytics warehouse or data lake destination",
            CatalogSpecies.MIRROR: "Read replica for load distribution",
            CatalogSpecies.CACHE: "Local or in-memory cache for performance",
            CatalogSpecies.CLONE: "Development or testing environment copy",
            CatalogSpecies.FORK: "Experimental or feature branch development",
        }
        return use_cases[self]


# Type alias for catalog species literals
CatalogSpeciesLiteral: TypeAlias = Literal[
    "SOURCE",
    "SINK",
    "MIRROR",
    "CACHE",
    "CLONE",
    "FORK",
]
