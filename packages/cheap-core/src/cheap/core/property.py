"""Property and PropertyDef protocols for Cheap data system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cheap.core.property_type import PropertyType, PropertyValue


@runtime_checkable
class PropertyDef(Protocol):
    """
    Protocol defining the structure and metadata of a property.

    A PropertyDef describes a property's name, type, and constraints,
    serving as a schema or template for actual property values.
    """

    @property
    def name(self) -> str:
        """
        Get the name of this property definition.

        Returns:
            The property name.
        """
        ...

    @property
    def property_type(self) -> PropertyType:
        """
        Get the data type of this property.

        Returns:
            The PropertyType defining what values are allowed.
        """
        ...

    @property
    def default_value(self) -> PropertyValue:
        """
        Get the default value for this property if not explicitly set.

        Returns:
            The default value, or None if no default is defined.
        """
        ...

    @property
    def has_default_value(self) -> bool:
        """
        Check if this property has a default value.

        Returns:
            True if a default value is defined.
        """
        ...

    @property
    def is_readable(self) -> bool:
        """
        Check if this property can be read.

        Returns:
            True if the property is readable.
        """
        ...

    @property
    def is_writable(self) -> bool:
        """
        Check if this property can be written.

        Returns:
            True if the property is writable.
        """
        ...

    @property
    def is_nullable(self) -> bool:
        """
        Check if this property can have a null/None value.

        Returns:
            True if null values are allowed.
        """
        ...

    @property
    def is_multivalued(self) -> bool:
        """
        Check if this property can hold multiple values.

        Returns:
            True if the property is multivalued (list/collection).
        """
        ...


@runtime_checkable
class Property(Protocol):
    """
    Protocol representing a single property value within an aspect.

    A Property combines a property definition (schema) with an actual value,
    providing type-safe access to structured data.
    """

    @property
    def definition(self) -> PropertyDef:
        """
        Get the definition (schema) for this property.

        Returns:
            The PropertyDef describing this property's structure.
        """
        ...

    @property
    def value(self) -> PropertyValue:
        """
        Get the current value of this property.

        Returns:
            The property value, which may be None if not set.
        """
        ...

    @value.setter
    def value(self, new_value: PropertyValue) -> None:
        """
        Set a new value for this property.

        Args:
            new_value: The new value to set.

        Raises:
            ValueError: If the value doesn't satisfy the property's constraints.
            TypeError: If the value type doesn't match the property type.
        """
        ...
