"""Hierarchy protocols for Cheap data system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from cheap.core.aspect import Aspect
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
    Protocol for flat directory-based hierarchies.

    Organizes entities with string keys in a single-level flat structure,
    like a flat directory or dictionary.
    """

    def put(self, key: str, entity_id: UUID) -> None:
        """
        Associate an entity with a key.

        Args:
            key: The string key.
            entity_id: The UUID of the entity.
        """
        ...

    def get(self, key: str) -> UUID | None:
        """
        Get the entity associated with a key.

        Args:
            key: The string key.

        Returns:
            The UUID of the entity, or None if key not found.
        """
        ...

    def remove(self, key: str) -> UUID | None:
        """
        Remove and return the entity at a key.

        Args:
            key: The string key.

        Returns:
            The UUID of the removed entity, or None if key not found.
        """
        ...

    def contains_key(self, key: str) -> bool:
        """
        Check if a key exists.

        Args:
            key: The string key to check.

        Returns:
            True if the key exists.
        """
        ...

    def keys(self) -> set[str]:
        """
        Get all keys in this directory.

        Returns:
            A set of all string keys.
        """
        ...


@runtime_checkable
class Node(Protocol):
    """
    Protocol representing a node in an EntityTreeHierarchy.

    A Node contains an entity ID and tracks parent-child relationships.
    """

    @property
    def entity_id(self) -> UUID:
        """
        Get the entity ID of this node.

        Returns:
            The UUID of the entity.
        """
        ...

    @property
    def parent(self) -> Node | None:
        """
        Get the parent node.

        Returns:
            The parent Node, or None if this is the root.
        """
        ...

    @property
    def children(self) -> list[Node]:
        """
        Get the child nodes.

        Returns:
            A list of child Node instances.
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
    def root(self) -> Node | None:
        """
        Get the root node of this tree.

        Returns:
            The root Node, or None if the tree is empty.
        """
        ...

    def get_node(self, entity_id: UUID) -> Node | None:
        """
        Get the node for a given entity ID.

        Args:
            entity_id: The UUID of the entity.

        Returns:
            The Node if found, None otherwise.
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

    def remove(self, entity_id: UUID) -> bool:
        """
        Remove an entity from the tree.

        Args:
            entity_id: The UUID of the entity to remove.

        Returns:
            True if the entity was removed, False if not found.
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


@runtime_checkable
class AspectMapHierarchy(Hierarchy, Protocol):
    """
    Protocol for aspect map hierarchies (UUID to Aspect mapping).

    Maps entity IDs (UUIDs) to Aspect objects, similar to dict[UUID, Aspect].
    """

    def put(self, entity_id: UUID, aspect: Aspect) -> None:
        """
        Associate an aspect with an entity ID.

        Args:
            entity_id: The UUID of the entity.
            aspect: The Aspect to associate.
        """
        ...

    def get(self, entity_id: UUID) -> Aspect | None:
        """
        Get the aspect associated with an entity ID.

        Args:
            entity_id: The UUID of the entity.

        Returns:
            The Aspect if found, None otherwise.
        """
        ...

    def remove(self, entity_id: UUID) -> Aspect | None:
        """
        Remove and return the aspect for an entity ID.

        Args:
            entity_id: The UUID of the entity.

        Returns:
            The removed Aspect, or None if not found.
        """
        ...

    def contains_key(self, entity_id: UUID) -> bool:
        """
        Check if an entity ID has an associated aspect.

        Args:
            entity_id: The UUID to check.

        Returns:
            True if the entity ID has an aspect.
        """
        ...

    def keys(self) -> set[UUID]:
        """
        Get all entity IDs in this map.

        Returns:
            A set of all entity UUIDs.
        """
        ...

    def values(self) -> list[Aspect]:
        """
        Get all aspects in this map.

        Returns:
            A list of all Aspect instances.
        """
        ...
