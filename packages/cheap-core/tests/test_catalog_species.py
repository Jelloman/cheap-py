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

    def test_is_read_only(self) -> None:
        """Test is_read_only property."""
        assert CatalogSpecies.MIRROR.is_read_only
        assert CatalogSpecies.CACHE.is_read_only
        assert not CatalogSpecies.SOURCE.is_read_only
        assert not CatalogSpecies.SINK.is_read_only
        assert not CatalogSpecies.CLONE.is_read_only
        assert not CatalogSpecies.FORK.is_read_only

    def test_is_writable(self) -> None:
        """Test is_writable property."""
        assert CatalogSpecies.SOURCE.is_writable
        assert CatalogSpecies.SINK.is_writable
        assert CatalogSpecies.CLONE.is_writable
        assert CatalogSpecies.FORK.is_writable
        assert not CatalogSpecies.MIRROR.is_writable
        assert not CatalogSpecies.CACHE.is_writable

    def test_is_authoritative(self) -> None:
        """Test is_authoritative property."""
        assert CatalogSpecies.SOURCE.is_authoritative
        assert not CatalogSpecies.SINK.is_authoritative
        assert not CatalogSpecies.MIRROR.is_authoritative
        assert not CatalogSpecies.CACHE.is_authoritative
        assert not CatalogSpecies.CLONE.is_authoritative
        assert not CatalogSpecies.FORK.is_authoritative

    def test_is_temporary(self) -> None:
        """Test is_temporary property."""
        assert CatalogSpecies.CACHE.is_temporary
        assert not CatalogSpecies.SOURCE.is_temporary
        assert not CatalogSpecies.SINK.is_temporary
        assert not CatalogSpecies.MIRROR.is_temporary
        assert not CatalogSpecies.CLONE.is_temporary
        assert not CatalogSpecies.FORK.is_temporary

    def test_is_replica(self) -> None:
        """Test is_replica property."""
        assert CatalogSpecies.MIRROR.is_replica
        assert CatalogSpecies.CACHE.is_replica
        assert CatalogSpecies.CLONE.is_replica
        assert not CatalogSpecies.SOURCE.is_replica
        assert not CatalogSpecies.SINK.is_replica
        assert not CatalogSpecies.FORK.is_replica

    def test_can_diverge(self) -> None:
        """Test can_diverge property."""
        assert CatalogSpecies.CLONE.can_diverge
        assert CatalogSpecies.FORK.can_diverge
        assert CatalogSpecies.CACHE.can_diverge
        assert not CatalogSpecies.SOURCE.can_diverge
        assert not CatalogSpecies.SINK.can_diverge
        assert not CatalogSpecies.MIRROR.can_diverge

    def test_source_characteristics(self) -> None:
        """Test that SOURCE has expected characteristics."""
        assert CatalogSpecies.SOURCE.is_authoritative
        assert CatalogSpecies.SOURCE.is_writable
        assert not CatalogSpecies.SOURCE.is_read_only
        assert not CatalogSpecies.SOURCE.is_temporary

    def test_mirror_characteristics(self) -> None:
        """Test that MIRROR has expected characteristics."""
        assert CatalogSpecies.MIRROR.is_read_only
        assert not CatalogSpecies.MIRROR.is_writable
        assert not CatalogSpecies.MIRROR.can_diverge
        assert CatalogSpecies.MIRROR.is_replica

    def test_cache_characteristics(self) -> None:
        """Test that CACHE has expected characteristics."""
        assert CatalogSpecies.CACHE.is_temporary
        assert CatalogSpecies.CACHE.is_read_only
        assert CatalogSpecies.CACHE.can_diverge

    def test_fork_characteristics(self) -> None:
        """Test that FORK has expected characteristics."""
        assert CatalogSpecies.FORK.can_diverge
        assert CatalogSpecies.FORK.is_writable
        assert not CatalogSpecies.FORK.is_replica
