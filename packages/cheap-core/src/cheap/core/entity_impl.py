"""Basic implementations of Entity protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast
from uuid import UUID, uuid4

from cheap.core.entity import Entity

if TYPE_CHECKING:
    from cheap.core.aspect import Aspect
    from cheap.core.aspect_impl import AspectImpl


@dataclass(slots=True)
class EntityImpl(Entity):
    """
    Basic mutable implementation of the Entity protocol.

    This class represents an entity with a unique ID and a collection
    of aspects that define its properties.
    """

    id: UUID = field(default_factory=uuid4)
    aspects: dict[str, AspectImpl] = field(default_factory=dict)

    def get_aspect(self, aspect_name: str) -> Aspect | None:
        """
        Get an aspect by name.

        Args:
            aspect_name: The name of the aspect to retrieve.

        Returns:
            The Aspect if found, None otherwise.
        """
        return cast("Aspect | None", self.aspects.get(aspect_name))

    def add_aspect(self, aspect: AspectImpl) -> None:
        """
        Add or replace an aspect in this entity.

        Args:
            aspect: The aspect to add.
        """
        self.aspects[aspect.definition.name] = aspect

    def remove_aspect(self, aspect_name: str) -> bool:
        """
        Remove an aspect from this entity.

        Args:
            aspect_name: The name of the aspect to remove.

        Returns:
            True if the aspect was removed, False if it didn't exist.
        """
        if aspect_name in self.aspects:
            del self.aspects[aspect_name]
            return True
        return False

    def has_aspect(self, aspect_name: str) -> bool:
        """
        Check if this entity has an aspect with the given name.

        Args:
            aspect_name: The aspect name to check.

        Returns:
            True if the aspect exists in this entity.
        """
        return aspect_name in self.aspects

    def aspect_names(self) -> set[str]:
        """
        Get the names of all aspects in this entity.

        Returns:
            A set of aspect names.
        """
        return set(self.aspects.keys())

    def aspect_count(self) -> int:
        """
        Get the number of aspects in this entity.

        Returns:
            The count of aspects.
        """
        return len(self.aspects)

    def clear_aspects(self) -> None:
        """Remove all aspects from this entity."""
        self.aspects.clear()

    def copy(self) -> EntityImpl:
        """
        Create a shallow copy of this entity with a new ID.

        Returns:
            A new Entity with the same aspects but a different ID.
        """
        return EntityImpl(id=uuid4(), aspects=self.aspects.copy())

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"EntityImpl(id={self.id}, aspects={len(self.aspects)})"
