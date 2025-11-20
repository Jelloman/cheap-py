"""Hierarchy type enum for Cheap data system."""

from __future__ import annotations

from enum import Enum
from typing import Final, Literal, TypeAlias


class HierarchyType(Enum):
    """
    Enumeration of supported hierarchy types in the Cheap system.

    Hierarchies organize entities in different structural patterns, each suited
    for different use cases and query patterns.
    """

    ENTITY_LIST = "ENTITY_LIST"
    """
    List hierarchy: Ordered collection of entities.
    Maintains insertion order and allows duplicates.
    """

    ENTITY_SET = "ENTITY_SET"
    """
    Set hierarchy: Unordered collection of unique entities.
    Ensures entity uniqueness, no guaranteed order.
    """

    ENTITY_DIR = "ENTITY_DIR"
    """
    Directory hierarchy: Entities organized in a directory-like structure.
    Supports path-based navigation with parent-child relationships.
    """

    ENTITY_TREE = "ENTITY_TREE"
    """
    Tree hierarchy: Entities organized in a tree structure.
    Single root with parent-child relationships, no cycles.
    """

    ASPECT_MAP = "ASPECT_MAP"
    """
    Aspect map hierarchy: Key-value mapping of aspects.
    Organizes entities by aspect keys rather than entity IDs.
    """

    def __str__(self) -> str:
        """Return the string representation of the hierarchy type."""
        return self.value

    def __repr__(self) -> str:
        """Return the detailed representation of the hierarchy type."""
        return f"HierarchyType.{self.name}"

    @property
    def is_ordered(self) -> bool:
        """
        Check if this hierarchy type maintains order.

        Returns:
            True if entities in this hierarchy type have a defined order.
        """
        return self in {HierarchyType.ENTITY_LIST, HierarchyType.ENTITY_TREE}

    @property
    def allows_duplicates(self) -> bool:
        """
        Check if this hierarchy type allows duplicate entities.

        Returns:
            True if entities can appear multiple times in this hierarchy.
        """
        return self == HierarchyType.ENTITY_LIST

    @property
    def is_hierarchical(self) -> bool:
        """
        Check if this hierarchy type has parent-child relationships.

        Returns:
            True if this hierarchy supports parent-child relationships.
        """
        return self in {HierarchyType.ENTITY_DIR, HierarchyType.ENTITY_TREE}

    @property
    def supports_paths(self) -> bool:
        """
        Check if this hierarchy type supports path-based navigation.

        Returns:
            True if paths can be used to navigate this hierarchy.
        """
        return self in {HierarchyType.ENTITY_DIR, HierarchyType.ENTITY_TREE}

    @property
    def is_key_based(self) -> bool:
        """
        Check if this hierarchy type uses keys for organization.

        Returns:
            True if this hierarchy organizes by keys (aspects).
        """
        return self == HierarchyType.ASPECT_MAP

    def get_description(self) -> str:
        """
        Get a human-readable description of this hierarchy type.

        Returns:
            A description of what this hierarchy type represents.
        """
        descriptions: Final[dict[HierarchyType, str]] = {
            HierarchyType.ENTITY_LIST: (
                "Ordered collection of entities, maintains insertion order, allows duplicates"
            ),
            HierarchyType.ENTITY_SET: (
                "Unordered collection of unique entities, no duplicates"
            ),
            HierarchyType.ENTITY_DIR: (
                "Directory-like structure with path-based navigation and parent-child relationships"
            ),
            HierarchyType.ENTITY_TREE: (
                "Tree structure with single root and parent-child relationships"
            ),
            HierarchyType.ASPECT_MAP: (
                "Key-value mapping organizing entities by aspect keys"
            ),
        }
        return descriptions[self]


# Type alias for hierarchy type literals
HierarchyTypeLiteral: TypeAlias = Literal[
    "ENTITY_LIST",
    "ENTITY_SET",
    "ENTITY_DIR",
    "ENTITY_TREE",
    "ASPECT_MAP",
]
