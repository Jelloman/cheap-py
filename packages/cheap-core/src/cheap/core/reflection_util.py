"""Reflection and introspection utilities for Python objects."""

from __future__ import annotations

import inspect
from dataclasses import Field, fields, is_dataclass
from typing import Any, get_args, get_origin

from cheap.core.property_type import PropertyType


class ReflectionUtil:
    """
    Utility class for introspecting Python objects and mapping them to CHEAP types.

    Provides methods for:
    - Type mapping from Python types to PropertyType
    - Dataclass field introspection
    - Property descriptor detection
    - Nullability analysis based on type hints
    """

    # Type mapping from Python types to PropertyType
    _TYPE_MAP: dict[type, PropertyType] = {
        # Boolean
        bool: PropertyType.BOOLEAN,
        # Integers
        int: PropertyType.BIG_INTEGER,  # Python int has unlimited precision
        # Floats
        float: PropertyType.FLOAT,
        # Strings
        str: PropertyType.STRING,
        # Binary
        bytes: PropertyType.BLOB,
        bytearray: PropertyType.BLOB,
    }

    @classmethod
    def map_type_to_property_type(cls, python_type: type) -> PropertyType:
        """
        Map a Python type to the corresponding PropertyType.

        Args:
            python_type: The Python type to map.

        Returns:
            The corresponding PropertyType, defaults to STRING for unmapped types.
        """
        # Handle direct mappings
        if python_type in cls._TYPE_MAP:
            return cls._TYPE_MAP[python_type]

        # Handle special imports that might not be in the default type map
        type_name = getattr(python_type, "__name__", str(python_type))

        # Check for datetime types
        if type_name in ("datetime", "date"):
            return PropertyType.DATE_TIME

        # Check for decimal types
        if type_name == "Decimal":
            return PropertyType.BIG_DECIMAL

        # Check for UUID
        if type_name == "UUID":
            return PropertyType.UUID

        # Default to STRING for unmapped types
        return PropertyType.STRING

    @staticmethod
    def is_dataclass_instance(obj: Any) -> bool:
        """
        Check if an object is a dataclass instance.

        Args:
            obj: The object to check.

        Returns:
            True if the object is a dataclass instance.
        """
        return is_dataclass(obj) and not isinstance(obj, type)

    @staticmethod
    def is_dataclass_type(obj_type: type) -> bool:
        """
        Check if a type is a dataclass.

        Args:
            obj_type: The type to check.

        Returns:
            True if the type is a dataclass.
        """
        return is_dataclass(obj_type)

    @staticmethod
    def get_dataclass_fields(obj: Any) -> tuple[Field[Any], ...]:
        """
        Get the fields of a dataclass.

        Args:
            obj: A dataclass instance or type.

        Returns:
            Tuple of Field objects describing the dataclass fields.

        Raises:
            TypeError: If obj is not a dataclass.
        """
        if not is_dataclass(obj):
            raise TypeError(f"{obj} is not a dataclass")
        return fields(obj)

    @staticmethod
    def is_optional_type(type_hint: Any) -> bool:
        """
        Check if a type hint represents an Optional type (Union with None).

        Args:
            type_hint: The type hint to check.

        Returns:
            True if the type hint allows None.

        Examples:
            >>> ReflectionUtil.is_optional_type(str | None)
            True
            >>> ReflectionUtil.is_optional_type(Optional[int])
            True
            >>> ReflectionUtil.is_optional_type(str)
            False
        """
        origin = get_origin(type_hint)

        # Check for Union types (includes Optional)
        if origin is not None:
            # Get the arguments of the Union
            args = get_args(type_hint)
            # Check if None is one of the arguments
            return type(None) in args

        return False

    @staticmethod
    def is_collection_type(type_hint: Any) -> bool:
        """
        Check if a type hint represents a collection (list, set, tuple, etc.).

        Args:
            type_hint: The type hint to check.

        Returns:
            True if the type hint is a collection type.

        Examples:
            >>> ReflectionUtil.is_collection_type(list[str])
            True
            >>> ReflectionUtil.is_collection_type(set[int])
            True
            >>> ReflectionUtil.is_collection_type(str)
            False
        """
        origin = get_origin(type_hint)

        if origin is None:
            # Check if it's a built-in collection type without subscript
            return type_hint in (list, set, tuple, frozenset)

        # Check if the origin is a collection type
        return origin in (list, set, tuple, frozenset)

    @staticmethod
    def get_collection_element_type(type_hint: Any) -> type | None:
        """
        Get the element type of a collection type hint.

        Args:
            type_hint: A collection type hint (e.g., list[str], set[int]).

        Returns:
            The element type, or None if not a parameterized collection.

        Examples:
            >>> ReflectionUtil.get_collection_element_type(list[str])
            <class 'str'>
            >>> ReflectionUtil.get_collection_element_type(list)
            None
        """
        origin = get_origin(type_hint)

        if origin in (list, set, tuple, frozenset):
            args = get_args(type_hint)
            if args:
                return args[0]

        return None

    @staticmethod
    def has_property_descriptor(obj_type: type, attr_name: str) -> bool:
        """
        Check if a class has a @property descriptor for an attribute.

        Args:
            obj_type: The class type to check.
            attr_name: The attribute name.

        Returns:
            True if the attribute is a property descriptor.
        """
        try:
            attr = getattr(obj_type, attr_name, None)
            return isinstance(attr, property)
        except AttributeError:
            return False

    @staticmethod
    def get_property_getter(obj_type: type, attr_name: str) -> Any:
        """
        Get the getter function of a @property descriptor.

        Args:
            obj_type: The class type.
            attr_name: The property name.

        Returns:
            The getter function, or None if not a property.
        """
        attr = getattr(obj_type, attr_name, None)
        if isinstance(attr, property):
            return attr.fget
        return None

    @staticmethod
    def get_property_setter(obj_type: type, attr_name: str) -> Any:
        """
        Get the setter function of a @property descriptor.

        Args:
            obj_type: The class type.
            attr_name: The property name.

        Returns:
            The setter function, or None if not a property or no setter defined.
        """
        attr = getattr(obj_type, attr_name, None)
        if isinstance(attr, property):
            return attr.fset
        return None

    @staticmethod
    def is_readonly_property(obj_type: type, attr_name: str) -> bool:
        """
        Check if a property descriptor is read-only (no setter).

        Args:
            obj_type: The class type.
            attr_name: The property name.

        Returns:
            True if the property exists but has no setter.
        """
        attr = getattr(obj_type, attr_name, None)
        if isinstance(attr, property):
            return attr.fset is None
        return False

    @classmethod
    def get_attribute_type(cls, obj_type: type, attr_name: str) -> type | None:
        """
        Get the type hint for an attribute.

        Args:
            obj_type: The class type.
            attr_name: The attribute name.

        Returns:
            The type hint, or None if not found.
        """
        # Check __annotations__ for type hints
        annotations = getattr(obj_type, "__annotations__", {})
        return annotations.get(attr_name)

    @classmethod
    def get_signature_return_type(cls, func: Any) -> type | None:
        """
        Get the return type annotation of a function.

        Args:
            func: The function to inspect.

        Returns:
            The return type, or None if not annotated.
        """
        try:
            sig = inspect.signature(func)
            if sig.return_annotation != inspect.Parameter.empty:
                return sig.return_annotation
        except (ValueError, TypeError):
            pass
        return None
