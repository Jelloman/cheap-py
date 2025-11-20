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

    def test_is_ordered(self) -> None:
        """Test is_ordered property."""
        assert HierarchyType.ENTITY_LIST.is_ordered
        assert HierarchyType.ENTITY_TREE.is_ordered
        assert not HierarchyType.ENTITY_SET.is_ordered
        assert not HierarchyType.ENTITY_DIR.is_ordered
        assert not HierarchyType.ASPECT_MAP.is_ordered

    def test_allows_duplicates(self) -> None:
        """Test allows_duplicates property."""
        assert HierarchyType.ENTITY_LIST.allows_duplicates
        assert not HierarchyType.ENTITY_SET.allows_duplicates
        assert not HierarchyType.ENTITY_DIR.allows_duplicates
        assert not HierarchyType.ENTITY_TREE.allows_duplicates
        assert not HierarchyType.ASPECT_MAP.allows_duplicates

    def test_is_hierarchical(self) -> None:
        """Test is_hierarchical property."""
        assert HierarchyType.ENTITY_DIR.is_hierarchical
        assert HierarchyType.ENTITY_TREE.is_hierarchical
        assert not HierarchyType.ENTITY_LIST.is_hierarchical
        assert not HierarchyType.ENTITY_SET.is_hierarchical
        assert not HierarchyType.ASPECT_MAP.is_hierarchical

    def test_supports_paths(self) -> None:
        """Test supports_paths property."""
        assert HierarchyType.ENTITY_DIR.supports_paths
        assert HierarchyType.ENTITY_TREE.supports_paths
        assert not HierarchyType.ENTITY_LIST.supports_paths
        assert not HierarchyType.ENTITY_SET.supports_paths
        assert not HierarchyType.ASPECT_MAP.supports_paths

    def test_is_key_based(self) -> None:
        """Test is_key_based property."""
        assert HierarchyType.ASPECT_MAP.is_key_based
        assert not HierarchyType.ENTITY_LIST.is_key_based
        assert not HierarchyType.ENTITY_SET.is_key_based
        assert not HierarchyType.ENTITY_DIR.is_key_based
        assert not HierarchyType.ENTITY_TREE.is_key_based

    def test_get_description(self) -> None:
        """Test get_description method returns non-empty strings."""
        for hierarchy_type in HierarchyType:
            description = hierarchy_type.get_description()
            assert isinstance(description, str)
            assert len(description) > 0

    def test_entity_list_description(self) -> None:
        """Test specific description for ENTITY_LIST."""
        desc = HierarchyType.ENTITY_LIST.get_description()
        assert "ordered" in desc.lower()
        assert "duplicates" in desc.lower()

    def test_entity_set_description(self) -> None:
        """Test specific description for ENTITY_SET."""
        desc = HierarchyType.ENTITY_SET.get_description()
        assert "unique" in desc.lower() or "duplicates" in desc.lower()

    def test_aspect_map_description(self) -> None:
        """Test specific description for ASPECT_MAP."""
        desc = HierarchyType.ASPECT_MAP.get_description()
        assert "key" in desc.lower() or "aspect" in desc.lower()
