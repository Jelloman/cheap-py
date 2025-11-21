"""Hierarchy type enum for Cheap data system."""

from __future__ import annotations

from enum import Enum
from typing import Literal, TypeAlias


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


# Type alias for hierarchy type literals
HierarchyTypeLiteral: TypeAlias = Literal[
    "ENTITY_LIST",
    "ENTITY_SET",
    "ENTITY_DIR",
    "ENTITY_TREE",
    "ASPECT_MAP",
]
