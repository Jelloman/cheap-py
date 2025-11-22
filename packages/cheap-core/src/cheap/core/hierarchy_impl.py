"""Basic implementations of Hierarchy protocols."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from cheap.core.aspect import Aspect
    from cheap.core.hierarchy_type import HierarchyType


@dataclass(slots=True)
class EntityListHierarchyImpl:
    """
    Implementation of EntityListHierarchy - ordered list allowing duplicates.

    Maintains insertion order and allows the same entity to appear multiple times.
    """

    name: str
    entities: list[UUID] = field(default_factory=list)

    @property
    def hierarchy_type(self) -> HierarchyType:
        """Get the type of this hierarchy."""
        from cheap.core.hierarchy_type import HierarchyType

        return HierarchyType.ENTITY_LIST

    def size(self) -> int:
        """Get the number of entities in this hierarchy."""
        return len(self.entities)

    def is_empty(self) -> bool:
        """Check if this hierarchy is empty."""
        return len(self.entities) == 0

    def clear(self) -> None:
        """Remove all entities from this hierarchy."""
        self.entities.clear()

    def add(self, entity_id: UUID) -> None:
        """
        Add an entity to the end of the list.

        Args:
            entity_id: The UUID of the entity to add.
        """
        self.entities.append(entity_id)

    def insert(self, index: int, entity_id: UUID) -> None:
        """
        Insert an entity at a specific position.

        Args:
            index: The position to insert at.
            entity_id: The UUID of the entity to insert.
        """
        self.entities.insert(index, entity_id)

    def remove(self, entity_id: UUID) -> bool:
        """
        Remove the first occurrence of an entity.

        Args:
            entity_id: The UUID of the entity to remove.

        Returns:
            True if the entity was removed, False otherwise.
        """
        try:
            self.entities.remove(entity_id)
            return True
        except ValueError:
            return False

    def get(self, index: int) -> UUID:
        """
        Get an entity at a specific index.

        Args:
            index: The index of the entity.

        Returns:
            The UUID at the specified index.

        Raises:
            IndexError: If the index is out of range.
        """
        return self.entities[index]

    def index_of(self, entity_id: UUID) -> int:
        """
        Get the index of the first occurrence of an entity.

        Args:
            entity_id: The UUID to find.

        Returns:
            The index, or -1 if not found.
        """
        try:
            return self.entities.index(entity_id)
        except ValueError:
            return -1

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"EntityListHierarchyImpl(name={self.name!r}, size={len(self.entities)})"


@dataclass(slots=True)
class EntitySetHierarchyImpl:
    """
    Implementation of EntitySetHierarchy - unordered set without duplicates.

    Ensures entity uniqueness with no guaranteed order.
    """

    name: str
    entities: set[UUID] = field(default_factory=set)

    @property
    def hierarchy_type(self) -> HierarchyType:
        """Get the type of this hierarchy."""
        from cheap.core.hierarchy_type import HierarchyType

        return HierarchyType.ENTITY_SET

    def size(self) -> int:
        """Get the number of entities in this hierarchy."""
        return len(self.entities)

    def is_empty(self) -> bool:
        """Check if this hierarchy is empty."""
        return len(self.entities) == 0

    def clear(self) -> None:
        """Remove all entities from this hierarchy."""
        self.entities.clear()

    def add(self, entity_id: UUID) -> bool:
        """
        Add an entity to the set.

        Args:
            entity_id: The UUID of the entity to add.

        Returns:
            True if the entity was added, False if it already existed.
        """
        size_before = len(self.entities)
        self.entities.add(entity_id)
        return len(self.entities) > size_before

    def remove(self, entity_id: UUID) -> bool:
        """
        Remove an entity from the set.

        Args:
            entity_id: The UUID of the entity to remove.

        Returns:
            True if the entity was removed, False if it didn't exist.
        """
        try:
            self.entities.remove(entity_id)
            return True
        except KeyError:
            return False

    def contains(self, entity_id: UUID) -> bool:
        """
        Check if an entity is in the set.

        Args:
            entity_id: The UUID to check.

        Returns:
            True if the entity exists in this hierarchy.
        """
        return entity_id in self.entities

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"EntitySetHierarchyImpl(name={self.name!r}, size={len(self.entities)})"


@dataclass(slots=True)
class EntityDirectoryHierarchyImpl:
    """
    Implementation of EntityDirectoryHierarchy - flat string-to-entity mapping.

    Provides a directory-like structure with path keys mapping to entity IDs.
    Note: This is a FLAT directory, not hierarchical.
    """

    name: str
    directory: dict[str, UUID] = field(default_factory=dict)

    @property
    def hierarchy_type(self) -> HierarchyType:
        """Get the type of this hierarchy."""
        from cheap.core.hierarchy_type import HierarchyType

        return HierarchyType.ENTITY_DIR

    def size(self) -> int:
        """Get the number of entities in this hierarchy."""
        return len(self.directory)

    def is_empty(self) -> bool:
        """Check if this hierarchy is empty."""
        return len(self.directory) == 0

    def clear(self) -> None:
        """Remove all entities from this hierarchy."""
        self.directory.clear()

    def put(self, path: str, entity_id: UUID) -> UUID | None:
        """
        Associate an entity with a path.

        Args:
            path: The path key.
            entity_id: The UUID of the entity.

        Returns:
            The previous UUID at this path, or None if there wasn't one.
        """
        old_value = self.directory.get(path)
        self.directory[path] = entity_id
        return old_value

    def get(self, path: str) -> UUID | None:
        """
        Get the entity ID for a path.

        Args:
            path: The path key to look up.

        Returns:
            The UUID if found, None otherwise.
        """
        return self.directory.get(path)

    def remove(self, path: str) -> UUID | None:
        """
        Remove and return the entity at a path.

        Args:
            path: The path key to remove.

        Returns:
            The removed UUID, or None if the path didn't exist.
        """
        return self.directory.pop(path, None)

    def contains_path(self, path: str) -> bool:
        """
        Check if a path exists in the directory.

        Args:
            path: The path to check.

        Returns:
            True if the path exists.
        """
        return path in self.directory

    def paths(self) -> set[str]:
        """
        Get all paths in the directory.

        Returns:
            A set of all path keys.
        """
        return set(self.directory.keys())

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"EntityDirectoryHierarchyImpl(name={self.name!r}, size={len(self.directory)})"


@dataclass(slots=True)
class NodeImpl:
    """
    Implementation of Node protocol for tree hierarchies.

    Represents a node in a tree with parent-child relationships.
    """

    entity_id: UUID
    parent: NodeImpl | None = None
    children: list[NodeImpl] = field(default_factory=list)

    def add_child(self, child: NodeImpl) -> None:
        """
        Add a child node.

        Args:
            child: The child node to add.
        """
        if child not in self.children:
            self.children.append(child)
            child.parent = self

    def remove_child(self, child: NodeImpl) -> bool:
        """
        Remove a child node.

        Args:
            child: The child node to remove.

        Returns:
            True if the child was removed, False otherwise.
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False

    def is_root(self) -> bool:
        """Check if this is a root node (no parent)."""
        return self.parent is None

    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"NodeImpl(entity_id={self.entity_id}, children={len(self.children)})"


@dataclass(slots=True)
class EntityTreeHierarchyImpl:
    """
    Implementation of EntityTreeHierarchy - tree structure with root node.

    Organizes entities in a tree with parent-child relationships.
    """

    name: str
    root: NodeImpl | None = None
    _nodes: dict[UUID, NodeImpl] = field(default_factory=dict)

    @property
    def hierarchy_type(self) -> HierarchyType:
        """Get the type of this hierarchy."""
        from cheap.core.hierarchy_type import HierarchyType

        return HierarchyType.ENTITY_TREE

    def size(self) -> int:
        """Get the number of entities in this hierarchy."""
        return len(self._nodes)

    def is_empty(self) -> bool:
        """Check if this hierarchy is empty."""
        return self.root is None

    def clear(self) -> None:
        """Remove all entities from this hierarchy."""
        self.root = None
        self._nodes.clear()

    def set_root(self, entity_id: UUID) -> None:
        """
        Set the root entity of the tree.

        Args:
            entity_id: The UUID of the root entity.
        """
        self.root = NodeImpl(entity_id=entity_id)
        self._nodes[entity_id] = self.root

    def add_child(self, parent_id: UUID, child_id: UUID) -> bool:
        """
        Add a child entity to a parent.

        Args:
            parent_id: The UUID of the parent entity.
            child_id: The UUID of the child entity.

        Returns:
            True if the child was added, False otherwise.
        """
        parent_node = self._nodes.get(parent_id)
        if parent_node is None:
            return False

        child_node = NodeImpl(entity_id=child_id)
        parent_node.add_child(child_node)
        self._nodes[child_id] = child_node
        return True

    def get_node(self, entity_id: UUID) -> NodeImpl | None:
        """
        Get the node for an entity.

        Args:
            entity_id: The UUID of the entity.

        Returns:
            The Node if found, None otherwise.
        """
        return self._nodes.get(entity_id)

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"EntityTreeHierarchyImpl(name={self.name!r}, size={len(self._nodes)})"


@dataclass(slots=True)
class AspectMapHierarchyImpl:
    """
    Implementation of AspectMapHierarchy - maps entity IDs to aspects.

    Organizes aspects by entity ID keys.
    """

    name: str
    aspects: dict[UUID, Aspect] = field(default_factory=dict)

    @property
    def hierarchy_type(self) -> HierarchyType:
        """Get the type of this hierarchy."""
        from cheap.core.hierarchy_type import HierarchyType

        return HierarchyType.ASPECT_MAP

    def size(self) -> int:
        """Get the number of aspects in this hierarchy."""
        return len(self.aspects)

    def is_empty(self) -> bool:
        """Check if this hierarchy is empty."""
        return len(self.aspects) == 0

    def clear(self) -> None:
        """Remove all aspects from this hierarchy."""
        self.aspects.clear()

    def put(self, entity_id: UUID, aspect: Aspect) -> Aspect | None:
        """
        Associate an aspect with an entity ID.

        Args:
            entity_id: The entity UUID key.
            aspect: The aspect to store.

        Returns:
            The previous aspect at this key, or None if there wasn't one.
        """
        old_value = self.aspects.get(entity_id)
        self.aspects[entity_id] = aspect
        return old_value

    def get(self, entity_id: UUID) -> Aspect | None:
        """
        Get the aspect for an entity ID.

        Args:
            entity_id: The entity UUID to look up.

        Returns:
            The aspect if found, None otherwise.
        """
        return self.aspects.get(entity_id)

    def remove(self, entity_id: UUID) -> Aspect | None:
        """
        Remove and return the aspect for an entity ID.

        Args:
            entity_id: The entity UUID to remove.

        Returns:
            The removed aspect, or None if it didn't exist.
        """
        return self.aspects.pop(entity_id, None)

    def contains_key(self, entity_id: UUID) -> bool:
        """
        Check if an entity ID exists in the map.

        Args:
            entity_id: The entity UUID to check.

        Returns:
            True if the key exists.
        """
        return entity_id in self.aspects

    def keys(self) -> set[UUID]:
        """
        Get all entity IDs in the map.

        Returns:
            A set of all entity UUID keys.
        """
        return set(self.aspects.keys())

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"AspectMapHierarchyImpl(name={self.name!r}, size={len(self.aspects)})"
