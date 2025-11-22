"""Basic implementations of Aspect and AspectDef protocols."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from cheap.core.aspect import AspectDef
    from cheap.core.entity import Entity
    from cheap.core.property import Property, PropertyDef
    from cheap.core.property_type import PropertyValue


@dataclass(frozen=True, slots=True)
class AspectDefImpl:
    """
    Basic immutable implementation of the AspectDef protocol.

    This class defines the structure of an aspect including its unique
    identifier, name, property definitions, and access control flags.
    """

    name: str
    properties: dict[str, PropertyDef] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    is_readable: bool = True
    is_writable: bool = True
    can_add_properties: bool = False
    can_remove_properties: bool = False

    def __post_init__(self) -> None:
        """Validate the aspect definition after initialization."""
        if not self.name:
            raise ValueError("Aspect name cannot be empty")

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"AspectDefImpl(id={self.id}, name={self.name!r}, properties={len(self.properties)})"


@dataclass(slots=True)
class AspectImpl:
    """
    Basic mutable implementation of the Aspect protocol.

    This class combines an aspect definition with property values,
    providing a property bag implementation.
    """

    definition: AspectDef
    properties: dict[str, Property] = field(default_factory=dict)
    entity: Entity | None = None

    def __post_init__(self) -> None:
        """Initialize properties from the aspect definition if needed."""
        # Ensure all defined properties exist
        for prop_name, prop_def in self.definition.properties.items():
            if prop_name not in self.properties:
                from cheap.core.property_impl import PropertyImpl

                self.properties[prop_name] = PropertyImpl(definition=prop_def)

    def get_property(self, property_name: str) -> Property | None:
        """
        Get a property by name.

        Args:
            property_name: The name of the property to retrieve.

        Returns:
            The Property if found, None otherwise.
        """
        return self.properties.get(property_name)

    def set_property(self, property_name: str, value: PropertyValue) -> None:
        """
        Set a property value.

        Args:
            property_name: The name of the property to set.
            value: The value to set.

        Raises:
            KeyError: If the property is not defined in this aspect.
            ValueError: If the value doesn't satisfy the property's constraints.
        """
        if property_name not in self.definition.properties:
            raise KeyError(
                f"Property '{property_name}' is not defined in aspect '{self.definition.name}'"
            )

        prop = self.properties.get(property_name)
        if prop is None:
            from cheap.core.property_impl import PropertyImpl

            prop_def = self.definition.properties[property_name]
            prop = PropertyImpl(definition=prop_def)
            self.properties[property_name] = prop

        prop.value = value

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"AspectImpl(definition={self.definition.name!r}, properties={len(self.properties)})"
