"""Tests for PropertyType enum."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from cheap.core.property_type import PropertyType


class TestPropertyType:
    """Test suite for PropertyType enum."""

    def test_enum_values(self) -> None:
        """Test that all expected enum values exist."""
        assert PropertyType.INTEGER.value == "INTEGER"
        assert PropertyType.FLOAT.value == "FLOAT"
        assert PropertyType.BIG_INTEGER.value == "BIG_INTEGER"
        assert PropertyType.BIG_DECIMAL.value == "BIG_DECIMAL"
        assert PropertyType.BOOLEAN.value == "BOOLEAN"
        assert PropertyType.STRING.value == "STRING"
        assert PropertyType.TEXT.value == "TEXT"
        assert PropertyType.DATE_TIME.value == "DATE_TIME"
        assert PropertyType.URI.value == "URI"
        assert PropertyType.UUID.value == "UUID"
        assert PropertyType.CLOB.value == "CLOB"
        assert PropertyType.BLOB.value == "BLOB"

    def test_string_representation(self) -> None:
        """Test string representation of enum values."""
        assert str(PropertyType.INTEGER) == "INTEGER"
        assert repr(PropertyType.INTEGER) == "PropertyType.INTEGER"

    def test_python_type_mapping(self) -> None:
        """Test that python_type property returns correct types."""
        assert PropertyType.INTEGER.python_type == int
        assert PropertyType.FLOAT.python_type == float
        assert PropertyType.BIG_INTEGER.python_type == int
        assert PropertyType.BIG_DECIMAL.python_type == Decimal
        assert PropertyType.BOOLEAN.python_type == bool
        assert PropertyType.STRING.python_type == str
        assert PropertyType.TEXT.python_type == str
        assert PropertyType.DATE_TIME.python_type == datetime
        assert PropertyType.URI.python_type == str
        assert PropertyType.UUID.python_type == UUID
        assert PropertyType.CLOB.python_type == str
        assert PropertyType.BLOB.python_type == bytes

    def test_validate_integers(self) -> None:
        """Test validation of integer values."""
        assert PropertyType.INTEGER.validate(42)
        assert PropertyType.INTEGER.validate(-100)
        assert PropertyType.INTEGER.validate(0)
        assert PropertyType.INTEGER.validate(None)
        assert not PropertyType.INTEGER.validate(3.14)
        assert not PropertyType.INTEGER.validate("42")

    def test_validate_floats(self) -> None:
        """Test validation of float values."""
        assert PropertyType.FLOAT.validate(3.14)
        assert PropertyType.FLOAT.validate(-2.5)
        assert PropertyType.FLOAT.validate(0.0)
        assert PropertyType.FLOAT.validate(None)
        assert not PropertyType.FLOAT.validate(42)
        assert not PropertyType.FLOAT.validate("3.14")

    def test_validate_booleans(self) -> None:
        """Test validation of boolean values."""
        assert PropertyType.BOOLEAN.validate(True)
        assert PropertyType.BOOLEAN.validate(False)
        assert PropertyType.BOOLEAN.validate(None)
        # Note: bool is subclass of int, so we must check bool first
        assert not PropertyType.BOOLEAN.validate(1)
        assert not PropertyType.BOOLEAN.validate("true")

    def test_validate_strings(self) -> None:
        """Test validation of string values."""
        assert PropertyType.STRING.validate("hello")
        assert PropertyType.STRING.validate("")
        assert PropertyType.STRING.validate(None)
        assert not PropertyType.STRING.validate(42)

    def test_validate_decimals(self) -> None:
        """Test validation of decimal values."""
        assert PropertyType.BIG_DECIMAL.validate(Decimal("123.45"))
        assert PropertyType.BIG_DECIMAL.validate(Decimal("0"))
        assert PropertyType.BIG_DECIMAL.validate(None)
        assert not PropertyType.BIG_DECIMAL.validate(123.45)
        assert not PropertyType.BIG_DECIMAL.validate(123)

    def test_validate_datetimes(self) -> None:
        """Test validation of datetime values."""
        now = datetime.now()
        assert PropertyType.DATE_TIME.validate(now)
        assert PropertyType.DATE_TIME.validate(None)
        assert not PropertyType.DATE_TIME.validate("2024-01-01")
        assert not PropertyType.DATE_TIME.validate(1234567890)

    def test_validate_uuids(self) -> None:
        """Test validation of UUID values."""
        test_uuid = uuid4()
        assert PropertyType.UUID.validate(test_uuid)
        assert PropertyType.UUID.validate(None)
        assert not PropertyType.UUID.validate(str(test_uuid))
        assert not PropertyType.UUID.validate("not-a-uuid")

    def test_validate_bytes(self) -> None:
        """Test validation of bytes values."""
        assert PropertyType.BLOB.validate(b"hello")
        assert PropertyType.BLOB.validate(b"")
        assert PropertyType.BLOB.validate(None)
        assert not PropertyType.BLOB.validate("hello")
        assert not PropertyType.BLOB.validate([1, 2, 3])

    def test_is_numeric(self) -> None:
        """Test is_numeric() method."""
        assert PropertyType.INTEGER.is_numeric()
        assert PropertyType.FLOAT.is_numeric()
        assert PropertyType.BIG_INTEGER.is_numeric()
        assert PropertyType.BIG_DECIMAL.is_numeric()
        assert not PropertyType.STRING.is_numeric()
        assert not PropertyType.BOOLEAN.is_numeric()

    def test_is_string(self) -> None:
        """Test is_string() method."""
        assert PropertyType.STRING.is_string()
        assert PropertyType.TEXT.is_string()
        assert PropertyType.CLOB.is_string()
        assert PropertyType.URI.is_string()
        assert not PropertyType.INTEGER.is_string()
        assert not PropertyType.BLOB.is_string()

    def test_is_binary(self) -> None:
        """Test is_binary() method."""
        assert PropertyType.BLOB.is_binary()
        assert not PropertyType.STRING.is_binary()
        assert not PropertyType.INTEGER.is_binary()

    def test_is_temporal(self) -> None:
        """Test is_temporal() method."""
        assert PropertyType.DATE_TIME.is_temporal()
        assert not PropertyType.STRING.is_temporal()
        assert not PropertyType.INTEGER.is_temporal()

    def test_from_value_integers(self) -> None:
        """Test inferring PropertyType from integer values."""
        assert PropertyType.from_value(42) == PropertyType.INTEGER
        assert PropertyType.from_value(-100) == PropertyType.INTEGER
        assert PropertyType.from_value(0) == PropertyType.INTEGER

    def test_from_value_floats(self) -> None:
        """Test inferring PropertyType from float values."""
        assert PropertyType.from_value(3.14) == PropertyType.FLOAT
        assert PropertyType.from_value(-2.5) == PropertyType.FLOAT

    def test_from_value_booleans(self) -> None:
        """Test inferring PropertyType from boolean values."""
        # Booleans must be checked before integers
        assert PropertyType.from_value(True) == PropertyType.BOOLEAN
        assert PropertyType.from_value(False) == PropertyType.BOOLEAN

    def test_from_value_strings(self) -> None:
        """Test inferring PropertyType from string values."""
        assert PropertyType.from_value("hello") == PropertyType.STRING
        assert PropertyType.from_value("") == PropertyType.STRING

    def test_from_value_decimals(self) -> None:
        """Test inferring PropertyType from Decimal values."""
        assert PropertyType.from_value(Decimal("123.45")) == PropertyType.BIG_DECIMAL

    def test_from_value_datetimes(self) -> None:
        """Test inferring PropertyType from datetime values."""
        assert PropertyType.from_value(datetime.now()) == PropertyType.DATE_TIME

    def test_from_value_uuids(self) -> None:
        """Test inferring PropertyType from UUID values."""
        assert PropertyType.from_value(uuid4()) == PropertyType.UUID

    def test_from_value_bytes(self) -> None:
        """Test inferring PropertyType from bytes values."""
        assert PropertyType.from_value(b"data") == PropertyType.BLOB

    def test_from_value_invalid(self) -> None:
        """Test that from_value raises TypeError for unsupported types."""
        with pytest.raises(TypeError, match="Cannot infer PropertyType"):
            PropertyType.from_value([1, 2, 3])

        with pytest.raises(TypeError, match="Cannot infer PropertyType"):
            PropertyType.from_value({"key": "value"})
