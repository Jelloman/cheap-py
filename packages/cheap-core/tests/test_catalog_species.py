"""Tests for CatalogSpecies enum."""

from cheap.core.catalog_species import CatalogSpecies


class TestCatalogSpecies:
    """Test suite for CatalogSpecies enum."""

    def test_enum_values(self) -> None:
        """Test that all expected enum values exist."""
        assert CatalogSpecies.SOURCE.value == "SOURCE"
        assert CatalogSpecies.SINK.value == "SINK"
        assert CatalogSpecies.MIRROR.value == "MIRROR"
        assert CatalogSpecies.CACHE.value == "CACHE"
        assert CatalogSpecies.CLONE.value == "CLONE"
        assert CatalogSpecies.FORK.value == "FORK"

    def test_string_representation(self) -> None:
        """Test string representation of enum values."""
        assert str(CatalogSpecies.SOURCE) == "SOURCE"
        assert repr(CatalogSpecies.SOURCE) == "CatalogSpecies.SOURCE"
