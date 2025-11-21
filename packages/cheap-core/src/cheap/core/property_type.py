"""Property type enum for Cheap data system."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Final, Literal, TypeAlias
from uuid import UUID

# Type aliases for property values
PropertyValue: TypeAlias = int | float | bool | str | Decimal | datetime | UUID | bytes | None


class PropertyType(Enum):
    """
    Enumeration of supported property value types in the Cheap system.

    Each property type corresponds to a specific Python type and provides
    validation and conversion capabilities.
    """

    # Numeric types
    INTEGER = "INTEGER"  # Python int (arbitrary precision)
    FLOAT = "FLOAT"  # Python float (64-bit)
    BIG_INTEGER = "BIG_INTEGER"  # Python int (alias for INTEGER)
    BIG_DECIMAL = "BIG_DECIMAL"  # Python Decimal (arbitrary precision decimal)

    # Boolean type
    BOOLEAN = "BOOLEAN"  # Python bool

    # String types
    STRING = "STRING"  # Short string (VARCHAR equivalent)
    TEXT = "TEXT"  # Long text (TEXT/CLOB equivalent)

    # Date/time types
    DATE_TIME = "DATE_TIME"  # Python datetime with timezone

    # Special types
    URI = "URI"  # URI/URL as string with validation
    UUID = "UUID"  # Python UUID

    # Binary types
    CLOB = "CLOB"  # Character large object (text)
    BLOB = "BLOB"  # Binary large object (bytes)

    def __str__(self) -> str:
        """Return the string representation of the property type."""
        return self.value

    def __repr__(self) -> str:
        """Return the detailed representation of the property type."""
        return f"PropertyType.{self.name}"

    @property
    def python_type(self) -> type[Any]:
        """
        Get the corresponding Python type for this property type.

        Returns:
            The Python type that corresponds to this PropertyType.
        """
        type_mapping: Final[dict[PropertyType, type[Any]]] = {
            PropertyType.INTEGER: int,
            PropertyType.FLOAT: float,
            PropertyType.BIG_INTEGER: int,
            PropertyType.BIG_DECIMAL: Decimal,
            PropertyType.BOOLEAN: bool,
            PropertyType.STRING: str,
            PropertyType.TEXT: str,
            PropertyType.DATE_TIME: datetime,
            PropertyType.URI: str,
            PropertyType.UUID: UUID,
            PropertyType.CLOB: str,
            PropertyType.BLOB: bytes,
        }
        return type_mapping[self]

    def validate(self, value: Any) -> bool:
        """
        Validate whether a value is compatible with this property type.

        Args:
            value: The value to validate.

        Returns:
            True if the value is compatible with this property type, False otherwise.
        """
        if value is None:
            return True  # None is valid for all property types

        expected_type = self.python_type
        return isinstance(value, expected_type)

    def is_numeric(self) -> bool:
        """
        Check if this property type represents a numeric value.

        Returns:
            True if this is a numeric type (INTEGER, FLOAT, BIG_INTEGER, BIG_DECIMAL).
        """
        return self in {
            PropertyType.INTEGER,
            PropertyType.FLOAT,
            PropertyType.BIG_INTEGER,
            PropertyType.BIG_DECIMAL,
        }

    def is_string(self) -> bool:
        """
        Check if this property type represents a string value.

        Returns:
            True if this is a string type (STRING, TEXT, CLOB, URI).
        """
        return self in {
            PropertyType.STRING,
            PropertyType.TEXT,
            PropertyType.CLOB,
            PropertyType.URI,
        }

    def is_binary(self) -> bool:
        """
        Check if this property type represents binary data.

        Returns:
            True if this is a binary type (BLOB).
        """
        return self == PropertyType.BLOB

    def is_temporal(self) -> bool:
        """
        Check if this property type represents a temporal value.

        Returns:
            True if this is a temporal type (DATE_TIME).
        """
        return self == PropertyType.DATE_TIME

    @classmethod
    def from_value(cls, value: Any) -> PropertyType:
        """
        Infer the property type from a Python value.

        Args:
            value: The value to infer the type from.

        Returns:
            The inferred PropertyType.

        Raises:
            TypeError: If the value type cannot be mapped to a PropertyType.
        """
        from datetime import datetime
        from decimal import Decimal
        from uuid import UUID

        if isinstance(value, bool):
            # Must check bool before int since bool is a subclass of int
            return PropertyType.BOOLEAN
        if isinstance(value, int):
            return PropertyType.INTEGER
        if isinstance(value, float):
            return PropertyType.FLOAT
        if isinstance(value, Decimal):
            return PropertyType.BIG_DECIMAL
        if isinstance(value, str):
            return PropertyType.STRING
        if isinstance(value, datetime):
            return PropertyType.DATE_TIME
        if isinstance(value, UUID):
            return PropertyType.UUID
        if isinstance(value, bytes):
            return PropertyType.BLOB

        raise TypeError(f"Cannot infer PropertyType from value of type {type(value)}")


# Type alias for property type literals
PropertyTypeLiteral: TypeAlias = Literal[
    "INTEGER",
    "FLOAT",
    "BIG_INTEGER",
    "BIG_DECIMAL",
    "BOOLEAN",
    "STRING",
    "TEXT",
    "DATE_TIME",
    "URI",
    "UUID",
    "CLOB",
    "BLOB",
]
