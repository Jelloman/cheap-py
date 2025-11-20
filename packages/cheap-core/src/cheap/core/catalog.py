"""Catalog and CatalogDef protocols for Cheap data system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from cheap.core.aspect import AspectDef
    from cheap.core.catalog_species import CatalogSpecies
    from cheap.core.entity import Entity
    from cheap.core.hierarchy import Hierarchy


@runtime_checkable
class HierarchyDef(Protocol):
    """
    Protocol defining the structure of a hierarchy.

    A HierarchyDef describes a hierarchy's name and type, serving as a schema.
    """

    @property
    def name(self) -> str:
        """
        Get the name of this hierarchy definition.

        Returns:
            The hierarchy name.
        """
        ...


@runtime_checkable
class CatalogDef(Protocol):
    """
    Protocol defining the structure and schema of a catalog.

    A CatalogDef contains the aspect definitions and hierarchy definitions
    that define the structure of catalog data. This is separate from Catalog
    instances which contain actual data.
    """

    @property
    def aspect_defs(self) -> dict[str, AspectDef]:
        """
        Get all aspect definitions in this catalog definition.

        Returns:
            A mapping from aspect names to their definitions.
        """
        ...

    @property
    def hierarchy_defs(self) -> dict[str, HierarchyDef]:
        """
        Get all hierarchy definitions in this catalog definition.

        Returns:
            A mapping from hierarchy names to their definitions.
        """
        ...


@runtime_checkable
class Catalog(Protocol):
    """
    Protocol representing a container for related entities and hierarchies.

    A Catalog is analogous to a database or repository, providing a coherent
    namespace for organizing entities and their relationships. It's the top-level
    container in the CHEAP model.
    """

    @property
    def name(self) -> str:
        """
        Get the name of this catalog.

        Returns:
            The catalog name.
        """
        ...

    @property
    def species(self) -> CatalogSpecies:
        """
        Get the species (type/role) of this catalog.

        Returns:
            The CatalogSpecies defining the catalog's role.
        """
        ...

    @property
    def version(self) -> str:
        """
        Get the version of this catalog.

        Returns:
            A version string (e.g., semantic version).
        """
        ...

    def get_entity(self, entity_id: UUID) -> Entity | None:
        """
        Get an entity by its unique ID.

        Args:
            entity_id: The UUID of the entity to retrieve.

        Returns:
            The Entity if found, None otherwise.
        """
        ...

    def add_entity(self, entity: Entity) -> None:
        """
        Add or update an entity in this catalog.

        Args:
            entity: The entity to add or update.

        Raises:
            ValueError: If the entity is not valid for this catalog.
        """
        ...

    def remove_entity(self, entity_id: UUID) -> bool:
        """
        Remove an entity from this catalog.

        Args:
            entity_id: The UUID of the entity to remove.

        Returns:
            True if the entity was removed, False if it didn't exist.
        """
        ...

    def has_entity(self, entity_id: UUID) -> bool:
        """
        Check if this catalog contains an entity with the given ID.

        Args:
            entity_id: The UUID to check.

        Returns:
            True if the entity exists in this catalog.
        """
        ...

    def entity_count(self) -> int:
        """
        Get the total number of entities in this catalog.

        Returns:
            The count of entities.
        """
        ...

    def all_entities(self) -> Iterable[Entity]:
        """
        Get an iterable of all entities in this catalog.

        Returns:
            An iterable of Entity instances.
        """
        ...

    def get_hierarchy(self, hierarchy_name: str) -> Hierarchy | None:
        """
        Get a hierarchy by name.

        Args:
            hierarchy_name: The name of the hierarchy to retrieve.

        Returns:
            The Hierarchy if found, None otherwise.
        """
        ...

    def add_hierarchy(self, hierarchy: Hierarchy) -> None:
        """
        Add or replace a hierarchy in this catalog.

        Args:
            hierarchy: The hierarchy to add.

        Raises:
            ValueError: If the hierarchy is not valid for this catalog.
        """
        ...

    def remove_hierarchy(self, hierarchy_name: str) -> bool:
        """
        Remove a hierarchy from this catalog.

        Args:
            hierarchy_name: The name of the hierarchy to remove.

        Returns:
            True if the hierarchy was removed, False if it didn't exist.
        """
        ...

    def has_hierarchy(self, hierarchy_name: str) -> bool:
        """
        Check if this catalog has a hierarchy with the given name.

        Args:
            hierarchy_name: The hierarchy name to check.

        Returns:
            True if the hierarchy exists in this catalog.
        """
        ...

    def hierarchy_names(self) -> set[str]:
        """
        Get the names of all hierarchies in this catalog.

        Returns:
            A set of hierarchy names.
        """
        ...

    def close(self) -> None:
        """
        Close this catalog and release any resources.

        After calling close(), the catalog should not be used.
        """
        ...
