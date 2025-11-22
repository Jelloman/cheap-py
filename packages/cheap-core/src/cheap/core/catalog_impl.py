"""Basic implementations of Catalog and CatalogDef protocols."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from cheap.core.catalog import Catalog, CatalogDef, HierarchyDef

if TYPE_CHECKING:
    from cheap.core.aspect import AspectDef
    from cheap.core.aspect_impl import AspectDefImpl
    from cheap.core.catalog_species import CatalogSpecies
    from cheap.core.hierarchy import (
        AspectMapHierarchy,
        EntityDirectoryHierarchy,
        EntityListHierarchy,
        EntitySetHierarchy,
        EntityTreeHierarchy,
        Hierarchy,
    )
    from cheap.core.hierarchy_type import HierarchyType


@dataclass(frozen=True, slots=True)
class HierarchyDefImpl(HierarchyDef):
    """
    Basic immutable implementation of the HierarchyDef protocol.

    Defines the structure of a hierarchy with its name and type.
    """

    name: str
    hierarchy_type: HierarchyType

    def __post_init__(self) -> None:
        """Validate the hierarchy definition after initialization."""
        if not self.name:
            raise ValueError("Hierarchy name cannot be empty")

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"HierarchyDefImpl(name={self.name!r}, type={self.hierarchy_type})"


@dataclass(frozen=True, slots=True)
class CatalogDefImpl(CatalogDef):
    """
    Basic immutable implementation of the CatalogDef protocol.

    Defines the structure and schema of a catalog with aspect and
    hierarchy definitions.
    """

    aspect_defs: dict[str, AspectDefImpl] = field(default_factory=dict)
    hierarchy_defs: dict[str, HierarchyDefImpl] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return (
            f"CatalogDefImpl(aspects={len(self.aspect_defs)}, "
            f"hierarchies={len(self.hierarchy_defs)})"
        )


@dataclass(slots=True)
class CatalogImpl(Catalog):
    """
    Basic mutable implementation of the Catalog protocol.

    A catalog is a container for related hierarchies and their schemas,
    providing a coherent namespace for organizing entities.
    """

    species: CatalogSpecies
    version: str
    global_id: UUID = field(default_factory=uuid4)
    uri: str | None = None
    upstream: Catalog | None = None
    _aspect_defs: dict[str, AspectDefImpl] = field(default_factory=dict)
    _hierarchies: dict[str, Hierarchy] = field(default_factory=dict)

    def add_aspect_def(self, aspect_def: AspectDef) -> None:
        """
        Add an aspect definition to this catalog.

        Args:
            aspect_def: The AspectDef to add.

        Raises:
            ValueError: If an AspectDef with the same name already exists.
        """
        if aspect_def.name in self._aspect_defs:
            raise ValueError(
                f"AspectDef '{aspect_def.name}' already exists in catalog"
            )
        self._aspect_defs[aspect_def.name] = aspect_def  # type: ignore

    def remove_aspect_def(self, aspect_name: str) -> bool:
        """
        Remove an aspect definition from this catalog.

        Args:
            aspect_name: The name of the aspect definition to remove.

        Returns:
            True if the AspectDef was removed, False if it didn't exist.
        """
        if aspect_name in self._aspect_defs:
            del self._aspect_defs[aspect_name]
            return True
        return False

    def get_hierarchy(self, hierarchy_name: str) -> Hierarchy | None:
        """
        Get a hierarchy by name.

        Args:
            hierarchy_name: The name of the hierarchy to retrieve.

        Returns:
            The Hierarchy if found, None otherwise.
        """
        return self._hierarchies.get(hierarchy_name)

    def add_hierarchy(self, hierarchy: Hierarchy) -> None:
        """
        Add or replace a hierarchy in this catalog.

        Args:
            hierarchy: The hierarchy to add.

        Raises:
            ValueError: If the hierarchy is not valid for this catalog.
        """
        self._hierarchies[hierarchy.name] = hierarchy

    def remove_hierarchy(self, hierarchy_name: str) -> bool:
        """
        Remove a hierarchy from this catalog.

        Args:
            hierarchy_name: The name of the hierarchy to remove.

        Returns:
            True if the hierarchy was removed, False if it didn't exist.
        """
        if hierarchy_name in self._hierarchies:
            del self._hierarchies[hierarchy_name]
            return True
        return False

    def has_hierarchy(self, hierarchy_name: str) -> bool:
        """
        Check if this catalog has a hierarchy with the given name.

        Args:
            hierarchy_name: The hierarchy name to check.

        Returns:
            True if the hierarchy exists in this catalog.
        """
        return hierarchy_name in self._hierarchies

    def hierarchy_names(self) -> set[str]:
        """
        Get the names of all hierarchies in this catalog.

        Returns:
            A set of hierarchy names.
        """
        return set(self._hierarchies.keys())

    def create_entity_list_hierarchy(self, name: str) -> EntityListHierarchy:
        """
        Create a new entity list hierarchy.

        Args:
            name: The name of the hierarchy.

        Returns:
            The newly created EntityListHierarchy.
        """
        from cheap.core.hierarchy_impl import EntityListHierarchyImpl

        hierarchy = EntityListHierarchyImpl(name=name, catalog=self, version=self.version)
        self.add_hierarchy(hierarchy)
        return hierarchy  # type: ignore

    def create_entity_set_hierarchy(self, name: str) -> EntitySetHierarchy:
        """
        Create a new entity set hierarchy.

        Args:
            name: The name of the hierarchy.

        Returns:
            The newly created EntitySetHierarchy.
        """
        from cheap.core.hierarchy_impl import EntitySetHierarchyImpl

        hierarchy = EntitySetHierarchyImpl(name=name, catalog=self, version=self.version)
        self.add_hierarchy(hierarchy)
        return hierarchy  # type: ignore

    def create_entity_directory_hierarchy(self, name: str) -> EntityDirectoryHierarchy:
        """
        Create a new entity directory hierarchy.

        Args:
            name: The name of the hierarchy.

        Returns:
            The newly created EntityDirectoryHierarchy.
        """
        from cheap.core.hierarchy_impl import EntityDirectoryHierarchyImpl

        hierarchy = EntityDirectoryHierarchyImpl(name=name, catalog=self, version=self.version)
        self.add_hierarchy(hierarchy)
        return hierarchy  # type: ignore

    def create_entity_tree_hierarchy(self, name: str) -> EntityTreeHierarchy:
        """
        Create a new entity tree hierarchy.

        Args:
            name: The name of the hierarchy.

        Returns:
            The newly created EntityTreeHierarchy.
        """
        from cheap.core.hierarchy_impl import EntityTreeHierarchyImpl

        hierarchy = EntityTreeHierarchyImpl(name=name, catalog=self, version=self.version)
        self.add_hierarchy(hierarchy)
        return hierarchy  # type: ignore

    def create_aspect_map_hierarchy(self, name: str) -> AspectMapHierarchy:
        """
        Create a new aspect map hierarchy.

        Args:
            name: The name of the hierarchy.

        Returns:
            The newly created AspectMapHierarchy.
        """
        from cheap.core.hierarchy_impl import AspectMapHierarchyImpl

        hierarchy = AspectMapHierarchyImpl(name=name, catalog=self, version=self.version)
        self.add_hierarchy(hierarchy)
        return hierarchy  # type: ignore

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return (
            f"CatalogImpl(global_id={self.global_id}, species={self.species}, "
            f"version={self.version!r}, hierarchies={len(self._hierarchies)})"
        )
