"""Dataclass-based aspect implementations using Python introspection."""

from __future__ import annotations

from dataclasses import MISSING, Field, fields
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from cheap.core.property_impl import PropertyDefImpl
from cheap.core.reflection_util import ReflectionUtil

if TYPE_CHECKING:
    from cheap.core.aspect import AspectDef
    from cheap.core.entity import Entity
    from cheap.core.property import Property, PropertyDef
    from cheap.core.property_type import PropertyValue


class DataclassAspectDef:
    """
    AspectDef implementation that introspects a Python dataclass type.

    This class analyzes a dataclass at runtime and creates PropertyDef objects
    for each dataclass field, mapping Python types to CHEAP PropertyTypes.

    Supports both frozen (immutable) and mutable dataclasses.
    """

    def __init__(
        self, dataclass_type: type[Any], name: str | None = None, aspect_id: UUID | None = None
    ) -> None:
        """
        Create an aspect definition from a dataclass type.

        Args:
            dataclass_type: The dataclass type to introspect.
            name: Optional name for the aspect (defaults to class name).
            aspect_id: Optional UUID for the aspect (auto-generated if not provided).

        Raises:
            TypeError: If dataclass_type is not a dataclass.
        """
        if not ReflectionUtil.is_dataclass_type(dataclass_type):
            raise TypeError(f"{dataclass_type} is not a dataclass")

        self._dataclass_type = dataclass_type
        self._name = name or dataclass_type.__name__
        self._id = aspect_id or uuid4()

        # Introspect the dataclass and build property definitions
        self._properties: dict[str, PropertyDef] = {}
        self._build_property_defs()

        # Determine mutability from dataclass metadata
        self._is_frozen = getattr(dataclass_type, "__dataclass_fields__", {}).get(
            list(fields(dataclass_type))[0].name if fields(dataclass_type) else None
        )
        # Check if this is a frozen dataclass
        dc_params = getattr(dataclass_type, "__dataclass_params__", None)
        self._is_frozen = dc_params.frozen if dc_params else False

    def _build_property_defs(self) -> None:
        """Build PropertyDef objects from dataclass fields."""
        for field in fields(self._dataclass_type):
            prop_def = self._create_property_def_from_field(field)
            self._properties[field.name] = prop_def

    def _create_property_def_from_field(self, field: Field[Any]) -> PropertyDef:
        """
        Create a PropertyDef from a dataclass Field.

        Args:
            field: The dataclass Field to convert.

        Returns:
            A PropertyDef matching the field's characteristics.
        """
        # Determine the base type (handling Optional)
        field_type = field.type
        is_nullable = ReflectionUtil.is_optional_type(field_type)

        # Check if it's a collection
        is_multivalued = ReflectionUtil.is_collection_type(field_type)

        # Get the actual type for mapping
        if is_multivalued:
            element_type = ReflectionUtil.get_collection_element_type(field_type)
            property_type = ReflectionUtil.map_type_to_property_type(element_type or object)
        else:
            # For Optional types, extract the non-None type
            if is_nullable:
                from typing import get_args

                args = get_args(field_type)
                # Get first non-None type
                actual_type = next((arg for arg in args if arg is not type(None)), object)
            else:
                actual_type = field_type

            # Handle forward references (strings) and Any
            if isinstance(actual_type, str) or actual_type is Any:
                mapped_type: type = object
            elif isinstance(actual_type, type):
                mapped_type = actual_type
            else:
                mapped_type = object

            property_type = ReflectionUtil.map_type_to_property_type(mapped_type)

        # Determine if field has a default value
        has_default = field.default is not MISSING or field.default_factory is not MISSING
        default_value = field.default if field.default is not MISSING else None

        # Frozen dataclasses are read-only
        is_writable = not self._is_frozen
        is_readable = True

        return PropertyDefImpl(
            name=field.name,
            property_type=property_type,
            default_value=default_value,
            has_default_value=has_default,
            is_readable=is_readable,
            is_writable=is_writable,
            is_nullable=is_nullable,
            is_multivalued=is_multivalued,
        )

    @property
    def id(self) -> UUID:
        """Get the unique ID of this aspect definition."""
        return self._id

    @property
    def name(self) -> str:
        """Get the name of this aspect."""
        return self._name

    @property
    def properties(self) -> dict[str, PropertyDef]:
        """Get the property definitions."""
        return self._properties

    @property
    def is_readable(self) -> bool:
        """Check if the aspect is readable."""
        return True

    @property
    def is_writable(self) -> bool:
        """Check if the aspect is writable (not frozen)."""
        return not self._is_frozen

    @property
    def can_add_properties(self) -> bool:
        """Check if properties can be added dynamically (always False for dataclasses)."""
        return False

    @property
    def can_remove_properties(self) -> bool:
        """Check if properties can be removed dynamically (always False for dataclasses)."""
        return False

    @property
    def dataclass_type(self) -> type[Any]:
        """Get the underlying dataclass type."""
        return self._dataclass_type


class DataclassAspect:
    """
    Aspect implementation that wraps a Python dataclass instance.

    Provides property-based access to dataclass fields through the CHEAP
    property model. Supports both frozen (read-only) and mutable dataclasses.

    For frozen dataclasses, all write operations raise ValueError.
    """

    def __init__(
        self, definition: DataclassAspectDef, instance: Any, entity: Entity | None = None
    ) -> None:
        """
        Create an aspect from a dataclass instance.

        Args:
            definition: The DataclassAspectDef describing this aspect.
            instance: The dataclass instance to wrap.
            entity: Optional entity this aspect belongs to.

        Raises:
            TypeError: If instance is not an instance of the dataclass type.
        """
        if not isinstance(instance, definition.dataclass_type):
            msg = (
                f"Instance must be of type {definition.dataclass_type}, "
                f"got {type(instance)}"
            )
            raise TypeError(msg)

        self._definition = definition
        self._instance = instance
        self._entity = entity

    @property
    def definition(self) -> AspectDef:
        """Get the aspect definition."""
        return self._definition  # type: ignore[return-value]

    @property
    def properties(self) -> dict[str, Property]:
        """
        Get properties (not supported for dataclass aspects).

        Dataclass aspects access fields directly rather than maintaining
        separate Property objects.

        Raises:
            NotImplementedError: This aspect uses direct field access.
        """
        msg = (
            "DataclassAspect accesses fields directly. "
            "Use get_property() to read field values."
        )
        raise NotImplementedError(msg)

    @property
    def entity(self) -> Entity | None:
        """Get the entity this aspect belongs to."""
        return self._entity

    def get_property(self, property_name: str) -> Property | None:
        """
        Get a property value by name.

        Args:
            property_name: The name of the property/field.

        Returns:
            A Property-like object wrapping the field value, or None if not found.
        """
        if property_name not in self._definition.properties:
            return None

        # Return a simple wrapper that provides the value
        from cheap.core.property_impl import PropertyImpl

        prop_def = self._definition.properties[property_name]
        value = getattr(self._instance, property_name, None)

        prop = PropertyImpl(definition=prop_def)
        if value is not None:
            prop.value = value

        return prop

    def set_property(self, property_name: str, value: PropertyValue) -> None:
        """
        Set a property value.

        Args:
            property_name: The name of the property/field.
            value: The value to set.

        Raises:
            KeyError: If the property is not defined.
            ValueError: If the dataclass is frozen (immutable).
            AttributeError: If the field cannot be set.
        """
        if property_name not in self._definition.properties:
            raise KeyError(f"Property '{property_name}' not defined in aspect '{self._definition.name}'")

        if not self._definition.is_writable:
            raise ValueError(
                f"Cannot set property '{property_name}' on frozen dataclass aspect '{self._definition.name}'"
            )

        setattr(self._instance, property_name, value)

    def read_property(self, property_name: str) -> PropertyValue:
        """
        Read a property value directly.

        Args:
            property_name: The name of the property/field.

        Returns:
            The property value.

        Raises:
            KeyError: If the property is not defined.
        """
        if property_name not in self._definition.properties:
            raise KeyError(f"Property '{property_name}' not defined in aspect '{self._definition.name}'")

        return getattr(self._instance, property_name)

    @property
    def instance(self) -> Any:
        """Get the underlying dataclass instance."""
        return self._instance

    def __repr__(self) -> str:
        """Return a string representation."""
        return f"DataclassAspect(definition={self._definition.name!r}, instance={self._instance!r})"
