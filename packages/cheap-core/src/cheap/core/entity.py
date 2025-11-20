"""Entity protocol for Cheap data system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from cheap.core.aspect import Aspect


@runtime_checkable
class Entity(Protocol):
    """
    Protocol representing an individual data item with a unique identifier.

    An Entity is the fundamental unit of data in the Cheap system, analogous to
    a row in a database, a document in a document store, or a node in a graph.
    Each entity has a unique ID and can have multiple aspects attached to it.
    """

    @property
    def id(self) -> UUID:
        """
        Get the unique identifier for this entity.

        Returns:
            A UUID uniquely identifying this entity across all catalogs.
        """
        ...

    @property
    def aspects(self) -> dict[str, Aspect]:
        """
        Get all aspects attached to this entity.

        Returns:
            A mapping from aspect names to Aspect instances.
        """
        ...

    def get_aspect(self, aspect_name: str) -> Aspect | None:
        """
        Get a specific aspect by name.

        Args:
            aspect_name: The name of the aspect to retrieve.

        Returns:
            The Aspect if found, None otherwise.
        """
        ...

    def add_aspect(self, aspect: Aspect) -> None:
        """
        Add or replace an aspect on this entity.

        Args:
            aspect: The aspect to add.

        Raises:
            TypeError: If the aspect is not valid.
        """
        ...

    def remove_aspect(self, aspect_name: str) -> bool:
        """
        Remove an aspect from this entity.

        Args:
            aspect_name: The name of the aspect to remove.

        Returns:
            True if the aspect was removed, False if it didn't exist.
        """
        ...

    def has_aspect(self, aspect_name: str) -> bool:
        """
        Check if this entity has an aspect with the given name.

        Args:
            aspect_name: The aspect name to check.

        Returns:
            True if the aspect exists on this entity.
        """
        ...

    def aspect_names(self) -> set[str]:
        """
        Get the names of all aspects on this entity.

        Returns:
            A set of aspect names.
        """
        ...

    def clear_aspects(self) -> None:
        """
        Remove all aspects from this entity.
        """
        ...

    def __eq__(self, other: object) -> bool:
        """
        Check equality based on entity ID.

        Args:
            other: The object to compare with.

        Returns:
            True if both are entities with the same ID.
        """
        ...

    def __hash__(self) -> int:
        """
        Get hash based on entity ID.

        Returns:
            Hash of the entity ID.
        """
        ...
