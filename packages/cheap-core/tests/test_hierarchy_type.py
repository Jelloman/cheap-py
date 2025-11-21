"""Tests for HierarchyType enum."""

from cheap.core.hierarchy_type import HierarchyType


class TestHierarchyType:
    """Test suite for HierarchyType enum."""

    def test_enum_values(self) -> None:
        """Test that all expected enum values exist."""
        assert HierarchyType.ENTITY_LIST.value == "ENTITY_LIST"
        assert HierarchyType.ENTITY_SET.value == "ENTITY_SET"
        assert HierarchyType.ENTITY_DIR.value == "ENTITY_DIR"
        assert HierarchyType.ENTITY_TREE.value == "ENTITY_TREE"
        assert HierarchyType.ASPECT_MAP.value == "ASPECT_MAP"

    def test_string_representation(self) -> None:
        """Test string representation of enum values."""
        assert str(HierarchyType.ENTITY_LIST) == "ENTITY_LIST"
        assert repr(HierarchyType.ENTITY_LIST) == "HierarchyType.ENTITY_LIST"
