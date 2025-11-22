"""Aspect and AspectDef protocols for Cheap data system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from cheap.core.entity import Entity
    from cheap.core.property import Property, PropertyDef
    from cheap.core.property_type import PropertyValue


@runtime_checkable
class AspectDef(Protocol):
    """
    Protocol defining the structure and metadata of an aspect.

    An AspectDef describes an aspect's name and the properties it contains,
    serving as a schema for aspect instances.
    """

    @property
    def id(self) -> UUID:
        """
        Get the unique identifier for this aspect definition.

        Returns:
            The UUID of this aspect definition.
        """
        ...

    @property
    def name(self) -> str:
        """
        Get the name of this aspect definition.

        Returns:
            The aspect name.
        """
        ...

    @property
    def properties(self) -> dict[str, PropertyDef]:
        """
        Get all property definitions in this aspect.

        Returns:
            A mapping from property names to their definitions.
        """
        ...

    @property
    def is_readable(self) -> bool:
        """
        Check if this aspect can be read.

        Returns:
            True if the aspect is readable.
        """
        ...

    @property
    def is_writable(self) -> bool:
        """
        Check if this aspect can be written.

        Returns:
            True if the aspect is writable.
        """
        ...

    @property
    def can_add_properties(self) -> bool:
        """
        Check if new properties can be added to this aspect.

        Returns:
            True if properties can be added dynamically.
        """
        ...

    @property
    def can_remove_properties(self) -> bool:
        """
        Check if properties can be removed from this aspect.

        Returns:
            True if properties can be removed dynamically.
        """
        ...


@runtime_checkable
class Aspect(Protocol):
    """
    Protocol representing a collection of properties associated with an entity.

    An Aspect is analogous to a row in a database table or a document in a
    document store, containing multiple named properties with typed values.
    """

    @property
    def definition(self) -> AspectDef:
        """
        Get the definition (schema) for this aspect.

        Returns:
            The AspectDef describing this aspect's structure.
        """
        ...

    @property
    def properties(self) -> dict[str, Property]:
        """
        Get all properties in this aspect.

        Returns:
            A mapping from property names to Property instances.
        """
        ...

    @property
    def entity(self) -> Entity | None:
        """
        Get the entity this aspect belongs to.

        Returns:
            The Entity that owns this aspect, or None if not attached.
        """
        ...

    def get_property(self, property_name: str) -> Property | None:
        """
        Get a specific property by name.

        Args:
            property_name: The name of the property to retrieve.

        Returns:
            The Property if found, None otherwise.
        """
        ...

    def set_property(self, property_name: str, value: PropertyValue) -> None:
        """
        Set the value of a property.

        Args:
            property_name: The name of the property to set.
            value: The value to assign to the property.

        Raises:
            KeyError: If the property is not defined in this aspect's schema.
            ValueError: If the value doesn't satisfy the property's constraints.
            TypeError: If the value type doesn't match the property type.
        """
        ...
