"""Hierarchy protocols for Cheap data system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from cheap.core.entity import Entity
    from cheap.core.hierarchy_type import HierarchyType


@runtime_checkable
class Hierarchy(Protocol):
    """
    Base protocol for all hierarchy types.

    A Hierarchy organizes entities in a specific structural pattern,
    defining relationships and providing navigation capabilities.
    """

    @property
    def name(self) -> str:
        """
        Get the name of this hierarchy.

        Returns:
            The hierarchy name.
        """
        ...

    @property
    def hierarchy_type(self) -> HierarchyType:
        """
        Get the type of this hierarchy.

        Returns:
            The HierarchyType defining this hierarchy's structure.
        """
        ...

    def contains(self, entity_id: UUID) -> bool:
        """
        Check if this hierarchy contains the given entity.

        Args:
            entity_id: The UUID of the entity to check.

        Returns:
            True if the entity is in this hierarchy.
        """
        ...

    def size(self) -> int:
        """
        Get the number of entities in this hierarchy.

        Returns:
            The count of entities.
        """
        ...

    def is_empty(self) -> bool:
        """
        Check if this hierarchy is empty.

        Returns:
            True if there are no entities in this hierarchy.
        """
        ...

    def clear(self) -> None:
        """
        Remove all entities from this hierarchy.
        """
        ...


@runtime_checkable
class EntityListHierarchy(Hierarchy, Protocol):
    """
    Protocol for list-based hierarchies (ordered, allows duplicates).

    Maintains entities in insertion order and allows the same entity
    to appear multiple times.
    """

    def add(self, entity_id: UUID) -> None:
        """
        Add an entity to the end of this list.

        Args:
            entity_id: The UUID of the entity to add.
        """
        ...

    def insert(self, index: int, entity_id: UUID) -> None:
        """
        Insert an entity at a specific position.

        Args:
            index: The position to insert at (0-based).
            entity_id: The UUID of the entity to insert.

        Raises:
            IndexError: If the index is out of bounds.
        """
        ...

    def remove_at(self, index: int) -> UUID:
        """
        Remove and return the entity at a specific position.

        Args:
            index: The position to remove from (0-based).

        Returns:
            The UUID of the removed entity.

        Raises:
            IndexError: If the index is out of bounds.
        """
        ...

    def get_at(self, index: int) -> UUID:
        """
        Get the entity at a specific position.

        Args:
            index: The position to get from (0-based).

        Returns:
            The UUID of the entity at that position.

        Raises:
            IndexError: If the index is out of bounds.
        """
        ...

    def index_of(self, entity_id: UUID) -> int:
        """
        Find the first index of an entity.

        Args:
            entity_id: The UUID to search for.

        Returns:
            The index of the first occurrence, or -1 if not found.
        """
        ...

    def all_entities(self) -> list[UUID]:
        """
        Get all entity IDs in order.

        Returns:
            A list of entity UUIDs in order.
        """
        ...


@runtime_checkable
class EntitySetHierarchy(Hierarchy, Protocol):
    """
    Protocol for set-based hierarchies (unordered, unique entities).

    Ensures each entity appears at most once, with no guaranteed order.
    """

    def add(self, entity_id: UUID) -> bool:
        """
        Add an entity to this set.

        Args:
            entity_id: The UUID of the entity to add.

        Returns:
            True if the entity was added, False if it was already present.
        """
        ...

    def remove(self, entity_id: UUID) -> bool:
        """
        Remove an entity from this set.

        Args:
            entity_id: The UUID of the entity to remove.

        Returns:
            True if the entity was removed, False if it wasn't present.
        """
        ...

    def all_entities(self) -> set[UUID]:
        """
        Get all entity IDs as a set.

        Returns:
            A set of entity UUIDs.
        """
        ...


@runtime_checkable
class EntityDirectoryHierarchy(Hierarchy, Protocol):
    """
    Protocol for directory-based hierarchies (path-based navigation).

    Organizes entities in a directory-like structure with paths,
    supporting parent-child relationships.
    """

    def add_at_path(self, path: str, entity_id: UUID) -> None:
        """
        Add an entity at a specific path.

        Args:
            path: The path where the entity should be added (e.g., "/folder/subfolder").
            entity_id: The UUID of the entity to add.

        Raises:
            ValueError: If the path is invalid.
        """
        ...

    def remove_at_path(self, path: str) -> UUID | None:
        """
        Remove and return the entity at a specific path.

        Args:
            path: The path to remove from.

        Returns:
            The UUID of the removed entity, or None if the path was empty.
        """
        ...

    def get_at_path(self, path: str) -> UUID | None:
        """
        Get the entity at a specific path.

        Args:
            path: The path to get from.

        Returns:
            The UUID of the entity at that path, or None if not found.
        """
        ...

    def list_children(self, path: str) -> list[str]:
        """
        List all immediate children of a path.

        Args:
            path: The parent path.

        Returns:
            A list of child paths.
        """
        ...

    def path_exists(self, path: str) -> bool:
        """
        Check if a path exists in this hierarchy.

        Args:
            path: The path to check.

        Returns:
            True if the path exists.
        """
        ...


@runtime_checkable
class EntityTreeHierarchy(Hierarchy, Protocol):
    """
    Protocol for tree-based hierarchies (single root, parent-child relationships).

    Organizes entities in a tree structure with a single root and
    parent-child relationships, ensuring no cycles.
    """

    @property
    def root(self) -> UUID | None:
        """
        Get the root entity of this tree.

        Returns:
            The UUID of the root entity, or None if the tree is empty.
        """
        ...

    def add_child(self, parent_id: UUID, child_id: UUID) -> None:
        """
        Add a child entity under a parent.

        Args:
            parent_id: The UUID of the parent entity.
            child_id: The UUID of the child entity to add.

        Raises:
            ValueError: If this would create a cycle or if parent doesn't exist.
        """
        ...

    def remove_subtree(self, entity_id: UUID) -> set[UUID]:
        """
        Remove an entity and all its descendants.

        Args:
            entity_id: The UUID of the entity to remove.

        Returns:
            A set of all removed entity UUIDs (including the entity itself).
        """
        ...

    def get_parent(self, entity_id: UUID) -> UUID | None:
        """
        Get the parent of an entity.

        Args:
            entity_id: The UUID of the entity.

        Returns:
            The UUID of the parent, or None if this is the root or not in tree.
        """
        ...

    def get_children(self, entity_id: UUID) -> list[UUID]:
        """
        Get all direct children of an entity.

        Args:
            entity_id: The UUID of the parent entity.

        Returns:
            A list of child entity UUIDs.
        """
        ...

    def get_descendants(self, entity_id: UUID) -> set[UUID]:
        """
        Get all descendants of an entity (children, grandchildren, etc.).

        Args:
            entity_id: The UUID of the ancestor entity.

        Returns:
            A set of all descendant entity UUIDs.
        """
        ...

    def get_ancestors(self, entity_id: UUID) -> list[UUID]:
        """
        Get all ancestors of an entity (parent, grandparent, etc.).

        Args:
            entity_id: The UUID of the descendant entity.

        Returns:
            A list of ancestor entity UUIDs, ordered from immediate parent to root.
        """
        ...


@runtime_checkable
class AspectMapHierarchy(Hierarchy, Protocol):
    """
    Protocol for aspect map hierarchies (key-value mapping by aspects).

    Organizes entities by aspect keys rather than entity IDs,
    allowing multiple entities to be associated with the same key.
    """

    def put(self, key: str, entity_id: UUID) -> None:
        """
        Associate an entity with a key.

        Args:
            key: The aspect key.
            entity_id: The UUID of the entity to associate.
        """
        ...

    def get(self, key: str) -> list[UUID]:
        """
        Get all entities associated with a key.

        Args:
            key: The aspect key to look up.

        Returns:
            A list of entity UUIDs associated with this key.
        """
        ...

    def remove_key(self, key: str) -> bool:
        """
        Remove all entities associated with a key.

        Args:
            key: The aspect key to remove.

        Returns:
            True if the key existed and was removed, False otherwise.
        """
        ...

    def has_key(self, key: str) -> bool:
        """
        Check if a key exists in this map.

        Args:
            key: The key to check.

        Returns:
            True if the key has any associated entities.
        """
        ...

    def all_keys(self) -> set[str]:
        """
        Get all keys in this map.

        Returns:
            A set of all keys that have associated entities.
        """
        ...
