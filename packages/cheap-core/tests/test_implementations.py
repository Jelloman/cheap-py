"""Tests for basic implementations of core protocols."""

from uuid import UUID, uuid4

import pytest

from cheap.core.aspect_impl import AspectDefImpl, AspectImpl
from cheap.core.catalog_impl import CatalogDefImpl, CatalogImpl, HierarchyDefImpl
from cheap.core.catalog_species import CatalogSpecies
from cheap.core.entity_impl import EntityImpl
from cheap.core.hierarchy_impl import (
    AspectMapHierarchyImpl,
    EntityDirectoryHierarchyImpl,
    EntityListHierarchyImpl,
    EntitySetHierarchyImpl,
    EntityTreeHierarchyImpl,
)
from cheap.core.hierarchy_type import HierarchyType
from cheap.core.property_impl import PropertyDefImpl, PropertyImpl
from cheap.core.property_type import PropertyType


class TestPropertyImpl:
    """Tests for PropertyDefImpl and PropertyImpl."""

    def test_property_def_creation(self) -> None:
        """Test creating a property definition."""
        prop_def = PropertyDefImpl(
            name="age", property_type=PropertyType.INTEGER, is_nullable=False
        )
        assert prop_def.name == "age"
        assert prop_def.property_type == PropertyType.INTEGER
        assert prop_def.is_nullable is False
        assert prop_def.is_readable is True

    def test_property_def_with_default(self) -> None:
        """Test property definition with default value."""
        prop_def = PropertyDefImpl(
            name="count",
            property_type=PropertyType.INTEGER,
            default_value=0,
        )
        assert prop_def.default_value == 0

    def test_property_def_invalid_default(self) -> None:
        """Test that invalid default values are rejected."""
        with pytest.raises(ValueError):
            PropertyDefImpl(
                name="age",
                property_type=PropertyType.INTEGER,
                default_value="not an int",
            )

    def test_property_get_set_value(self) -> None:
        """Test getting and setting property values."""
        prop_def = PropertyDefImpl(name="name", property_type=PropertyType.STRING)
        prop = PropertyImpl(definition=prop_def)

        prop.value = "Alice"
        assert prop.value == "Alice"

    def test_property_read_only(self) -> None:
        """Test that read-only properties cannot be changed."""
        prop_def = PropertyDefImpl(name="id", property_type=PropertyType.UUID, is_writable=False)
        prop = PropertyImpl(definition=prop_def)

        test_id = uuid4()

        with pytest.raises(ValueError, match="read-only"):
            prop.value = test_id

    def test_property_not_nullable(self) -> None:
        """Test that non-nullable properties cannot be set to None."""
        prop_def = PropertyDefImpl(
            name="name", property_type=PropertyType.STRING, is_nullable=False
        )
        prop = PropertyImpl(definition=prop_def)

        with pytest.raises(ValueError, match="nullable"):
            prop.value = None


class TestAspectImpl:
    """Tests for AspectDefImpl and AspectImpl."""

    def test_aspect_def_creation(self) -> None:
        """Test creating an aspect definition."""
        aspect_def = AspectDefImpl(name="person")
        assert aspect_def.name == "person"
        assert isinstance(aspect_def.id, UUID)
        assert len(aspect_def.properties) == 0

    def test_aspect_def_with_properties(self) -> None:
        """Test aspect definition with properties."""
        prop_def1 = PropertyDefImpl(name="name", property_type=PropertyType.STRING)
        prop_def2 = PropertyDefImpl(name="age", property_type=PropertyType.INTEGER)

        aspect_def = AspectDefImpl(name="person", properties={"name": prop_def1, "age": prop_def2})
        assert len(aspect_def.properties) == 2
        assert "name" in aspect_def.properties
        assert "age" in aspect_def.properties

    def test_aspect_get_set_property(self) -> None:
        """Test getting and setting properties on an aspect."""
        prop_def = PropertyDefImpl(name="name", property_type=PropertyType.STRING)
        aspect_def = AspectDefImpl(name="person", properties={"name": prop_def})

        aspect = AspectImpl(definition=aspect_def)
        aspect.set_property("name", "Bob")

        prop = aspect.get_property("name")
        assert prop is not None
        assert prop.value == "Bob"

    def test_aspect_undefined_property(self) -> None:
        """Test that setting undefined properties raises an error."""
        aspect_def = AspectDefImpl(name="person")
        aspect = AspectImpl(definition=aspect_def)

        with pytest.raises(KeyError):
            aspect.set_property("undefined", "value")


class TestEntityImpl:
    """Tests for EntityImpl."""

    def test_entity_creation(self) -> None:
        """Test creating an entity."""
        entity = EntityImpl()
        assert isinstance(entity.id, UUID)
        assert len(entity.aspects) == 0

    def test_entity_add_aspect(self) -> None:
        """Test adding aspects to an entity."""
        aspect_def = AspectDefImpl(name="person")
        aspect = AspectImpl(definition=aspect_def)

        entity = EntityImpl()
        entity.add_aspect(aspect)

        assert entity.has_aspect("person")
        assert entity.aspect_count() == 1

    def test_entity_remove_aspect(self) -> None:
        """Test removing aspects from an entity."""
        aspect_def = AspectDefImpl(name="person")
        aspect = AspectImpl(definition=aspect_def)

        entity = EntityImpl()
        entity.add_aspect(aspect)
        assert entity.remove_aspect("person") is True
        assert entity.has_aspect("person") is False
        assert entity.remove_aspect("person") is False


class TestHierarchyImpl:
    """Tests for hierarchy implementations."""

    def test_entity_list_hierarchy(self) -> None:
        """Test EntityListHierarchyImpl."""
        hierarchy = EntityListHierarchyImpl(name="list1")
        assert hierarchy.hierarchy_type == HierarchyType.ENTITY_LIST

        id1 = uuid4()
        id2 = uuid4()

        hierarchy.add(id1)
        hierarchy.add(id2)
        hierarchy.add(id1)  # Duplicates allowed

        assert hierarchy.size() == 3
        assert hierarchy.get(0) == id1
        assert hierarchy.get(1) == id2
        assert hierarchy.get(2) == id1

    def test_entity_set_hierarchy(self) -> None:
        """Test EntitySetHierarchyImpl."""
        hierarchy = EntitySetHierarchyImpl(name="set1")
        assert hierarchy.hierarchy_type == HierarchyType.ENTITY_SET

        id1 = uuid4()
        id2 = uuid4()

        assert hierarchy.add(id1) is True
        assert hierarchy.add(id2) is True
        assert hierarchy.add(id1) is False  # Duplicates not allowed

        assert hierarchy.size() == 2
        assert hierarchy.contains(id1)

    def test_entity_directory_hierarchy(self) -> None:
        """Test EntityDirectoryHierarchyImpl."""
        hierarchy = EntityDirectoryHierarchyImpl(name="dir1")
        assert hierarchy.hierarchy_type == HierarchyType.ENTITY_DIR

        id1 = uuid4()
        id2 = uuid4()

        hierarchy.put("/users/alice", id1)
        hierarchy.put("/users/bob", id2)

        assert hierarchy.size() == 2
        assert hierarchy.get("/users/alice") == id1
        assert hierarchy.contains_path("/users/bob")

    def test_entity_tree_hierarchy(self) -> None:
        """Test EntityTreeHierarchyImpl."""
        hierarchy = EntityTreeHierarchyImpl(name="tree1")
        assert hierarchy.hierarchy_type == HierarchyType.ENTITY_TREE

        root_id = uuid4()
        child_id = uuid4()

        hierarchy.set_root(root_id)
        assert hierarchy.is_empty() is False

        hierarchy.add_child(root_id, child_id)
        assert hierarchy.size() == 2

        node = hierarchy.get_node(child_id)
        assert node is not None
        assert node.entity_id == child_id

    def test_aspect_map_hierarchy(self) -> None:
        """Test AspectMapHierarchyImpl."""
        hierarchy = AspectMapHierarchyImpl(name="map1")
        assert hierarchy.hierarchy_type == HierarchyType.ASPECT_MAP

        id1 = uuid4()
        aspect_def = AspectDefImpl(name="person")
        aspect = AspectImpl(definition=aspect_def)

        hierarchy.put(id1, aspect)
        assert hierarchy.size() == 1
        assert hierarchy.get(id1) == aspect
        assert hierarchy.contains_key(id1)


class TestCatalogImpl:
    """Tests for CatalogDefImpl and CatalogImpl."""

    def test_hierarchy_def_creation(self) -> None:
        """Test creating a hierarchy definition."""
        hierarchy_def = HierarchyDefImpl(name="entities", hierarchy_type=HierarchyType.ENTITY_LIST)
        assert hierarchy_def.name == "entities"
        assert hierarchy_def.hierarchy_type == HierarchyType.ENTITY_LIST

    def test_catalog_def_creation(self) -> None:
        """Test creating a catalog definition."""
        catalog_def = CatalogDefImpl()
        assert len(catalog_def.aspect_defs) == 0
        assert len(catalog_def.hierarchy_defs) == 0

    def test_catalog_creation(self) -> None:
        """Test creating a catalog."""
        catalog = CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0")
        assert isinstance(catalog.global_id, UUID)
        assert catalog.species == CatalogSpecies.SOURCE
        assert catalog.version == "1.0.0"
        assert catalog.uri is None
        assert catalog.upstream is None

    def test_catalog_add_aspect_def(self) -> None:
        """Test adding aspect definitions to a catalog."""
        catalog = CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0")
        aspect_def = AspectDefImpl(name="person")

        catalog.add_aspect_def(aspect_def)

        # Should raise error when adding duplicate
        with pytest.raises(ValueError, match="already exists"):
            catalog.add_aspect_def(aspect_def)

    def test_catalog_hierarchies(self) -> None:
        """Test managing hierarchies in a catalog."""
        catalog = CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0")
        hierarchy = EntityListHierarchyImpl(name="entities")

        catalog.add_hierarchy(hierarchy)
        assert catalog.has_hierarchy("entities")
        assert catalog.hierarchy_names() == {"entities"}

        retrieved = catalog.get_hierarchy("entities")
        assert retrieved == hierarchy

        assert catalog.remove_hierarchy("entities") is True
        assert catalog.has_hierarchy("entities") is False
