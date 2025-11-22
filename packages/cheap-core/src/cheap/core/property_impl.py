"""Basic implementations of Property and PropertyDef protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from cheap.core.property import Property, PropertyDef

if TYPE_CHECKING:
    from cheap.core.property_type import PropertyType, PropertyValue


@dataclass(frozen=True, slots=True)
class PropertyDefImpl(PropertyDef):
    """
    Basic immutable implementation of the PropertyDef protocol.

    This class provides a simple, immutable property definition
    with name, type, and constraint information matching the Java implementation.
    """

    name: str
    property_type: PropertyType
    default_value: PropertyValue = None
    has_default_value: bool = False
    is_readable: bool = True
    is_writable: bool = True
    is_nullable: bool = True
    is_multivalued: bool = False

    def __post_init__(self) -> None:
        """Validate the property definition after initialization."""
        if not self.name:
            raise ValueError("Property name cannot be empty")
        if self.default_value is not None and not self.property_type.validate(self.default_value):
            raise ValueError(
                f"Default value {self.default_value} is not valid for type {self.property_type}"
            )


@dataclass(slots=True)
class PropertyImpl(Property):
    """
    Basic mutable implementation of the Property protocol.

    This class combines a property definition with a value,
    allowing the value to be changed while maintaining the schema.
    """

    definition: PropertyDefImpl
    _value: PropertyValue = None

    @property
    def value(self) -> PropertyValue:
        """
        Get the current value of this property.

        Returns:
            The property value, or the default value if not set.
        """
        if self._value is None:
            return self.definition.default_value
        return self._value

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
        if not self.definition.is_writable:
            raise ValueError(f"Cannot write to read-only property '{self.definition.name}'")

        if new_value is not None:
            if not self.definition.property_type.validate(new_value):
                raise TypeError(
                    f"Value {new_value} is not valid for property type {self.definition.property_type}"
                )
        elif not self.definition.is_nullable:
            raise ValueError(f"Cannot set non-nullable property '{self.definition.name}' to None")

        self._value = new_value

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return (
            f"PropertyImpl(name={self.definition.name!r}, "
            f"type={self.definition.property_type}, value={self.value!r})"
        )
