"""Aspect and AspectDef protocols for Cheap data system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Protocol, runtime_checkable

if TYPE_CHECKING:
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

    def get_property_def(self, property_name: str) -> PropertyDef | None:
        """
        Get a specific property definition by name.

        Args:
            property_name: The name of the property to retrieve.

        Returns:
            The PropertyDef if found, None otherwise.
        """
        ...

    def has_property(self, property_name: str) -> bool:
        """
        Check if this aspect defines a property with the given name.

        Args:
            property_name: The property name to check.

        Returns:
            True if the property is defined in this aspect.
        """
        ...

    @property
    def required_properties(self) -> set[str]:
        """
        Get the names of all required properties in this aspect.

        Returns:
            A set of property names that must have values.
        """
        ...

    @property
    def description(self) -> str | None:
        """
        Get a human-readable description of this aspect.

        Returns:
            A description of the aspect, or None if not available.
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
    def name(self) -> str:
        """
        Get the name of this aspect (convenience accessor).

        Returns:
            The aspect name from its definition.
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

    def get_value(self, property_name: str) -> PropertyValue:
        """
        Get the value of a property (convenience method).

        Args:
            property_name: The name of the property.

        Returns:
            The property value, or None if not set or not found.
        """
        ...

    def has_property(self, property_name: str) -> bool:
        """
        Check if this aspect has a property with the given name.

        Args:
            property_name: The property name to check.

        Returns:
            True if the property exists in this aspect.
        """
        ...

    def clear_property(self, property_name: str) -> None:
        """
        Clear the value of a property, resetting it to default or None.

        Args:
            property_name: The name of the property to clear.
        """
        ...

    def property_names(self) -> Iterable[str]:
        """
        Get an iterable of all property names in this aspect.

        Returns:
            An iterable of property names.
        """
        ...

    def validate(self) -> bool:
        """
        Validate that all properties satisfy their constraints.

        Returns:
            True if all property values are valid and all required properties are set.
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this aspect to a dictionary representation.

        Returns:
            A dictionary mapping property names to their values.
        """
        ...

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """
        Update property values from a dictionary.

        Args:
            data: A dictionary mapping property names to values.

        Raises:
            KeyError: If a property name in the dict is not defined in this aspect.
            ValueError: If a value doesn't satisfy its property's constraints.
            TypeError: If a value type doesn't match its property type.
        """
        ...
