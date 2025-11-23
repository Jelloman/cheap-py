"""Tests for CHEAP JSON serialization."""

from __future__ import annotations

from uuid import UUID, uuid4

import orjson
from cheap.core.aspect_impl import AspectDefImpl, AspectImpl
from cheap.core.catalog_impl import CatalogDefImpl, CatalogImpl, HierarchyDefImpl
from cheap.core.catalog_species import CatalogSpecies
from cheap.core.entity_impl import EntityImpl
from cheap.core.hierarchy_type import HierarchyType
from cheap.core.property_impl import PropertyDefImpl
from cheap.core.property_type import PropertyType
from cheap.json.deserializer import CheapJsonDeserializer
from cheap.json.serializer import CheapJsonSerializer


class TestPropertyDefSerialization:
    """Test PropertyDef serialization and deserialization."""

    def test_serialize_simple_property_def(self) -> None:
        """Test serializing a simple PropertyDef."""
        prop_def = PropertyDefImpl(
            name="age",
            property_type=PropertyType.INTEGER,
        )

        json_bytes = CheapJsonSerializer.to_json(prop_def)
        data = orjson.loads(json_bytes)

        assert data["name"] == "age"
        assert data["type"] == "INTEGER"
        # Default values should not be included
        assert "isWritable" not in data
        assert "isNullable" not in data

    def test_serialize_property_def_with_options(self) -> None:
        """Test serializing a PropertyDef with non-default options."""
        prop_def = PropertyDefImpl(
            name="description",
            property_type=PropertyType.TEXT,
            is_nullable=True,
            is_writable=False,
            default_value="N/A",
        )

        json_bytes = CheapJsonSerializer.to_json(prop_def)
        data = orjson.loads(json_bytes)

        assert data["name"] == "description"
        assert data["type"] == "TEXT"
        assert data["isNullable"] is True
        assert data["isWritable"] is False
        assert data["defaultValue"] == "N/A"

    def test_roundtrip_property_def(self) -> None:
        """Test PropertyDef roundtrip serialization."""
        original = PropertyDefImpl(
            name="count",
            property_type=PropertyType.BIG_INTEGER,
            is_nullable=True,
            min_value=0,
            max_value=1000,
        )

        # Serialize
        json_bytes = CheapJsonSerializer.to_json(original)

        # Deserialize
        deserialized = CheapJsonDeserializer.from_json_property_def(json_bytes)

        assert deserialized.name == original.name
        assert deserialized.property_type == original.property_type
        assert deserialized.is_nullable == original.is_nullable
        assert deserialized.min_value == original.min_value
        assert deserialized.max_value == original.max_value


class TestAspectDefSerialization:
    """Test AspectDef serialization and deserialization."""

    def test_serialize_aspect_def(self) -> None:
        """Test serializing an AspectDef."""
        prop1 = PropertyDefImpl(name="name", property_type=PropertyType.STRING)
        prop2 = PropertyDefImpl(name="age", property_type=PropertyType.INTEGER)

        aspect_def = AspectDefImpl(
            name="person",
            properties={"name": prop1, "age": prop2},
        )

        json_bytes = CheapJsonSerializer.to_json(aspect_def)
        data = orjson.loads(json_bytes)

        assert data["name"] == "person"
        assert "id" in data
        assert "properties" in data
        assert "name" in data["properties"]
        assert "age" in data["properties"]

    def test_roundtrip_aspect_def(self) -> None:
        """Test AspectDef roundtrip serialization."""
        prop1 = PropertyDefImpl(name="email", property_type=PropertyType.STRING)
        prop2 = PropertyDefImpl(name="active", property_type=PropertyType.BOOLEAN)

        original = AspectDefImpl(
            name="user",
            properties={"email": prop1, "active": prop2},
            can_add_properties=False,
        )

        # Serialize
        json_bytes = CheapJsonSerializer.to_json(original)

        # Deserialize
        deserialized = CheapJsonDeserializer.from_json_aspect_def(json_bytes)

        assert deserialized.name == original.name
        assert len(deserialized.properties) == 2
        assert "email" in deserialized.properties
        assert "active" in deserialized.properties
        assert deserialized.can_add_properties == original.can_add_properties


class TestAspectSerialization:
    """Test Aspect serialization and deserialization."""

    def test_serialize_aspect(self) -> None:
        """Test serializing an Aspect."""
        prop_def1 = PropertyDefImpl(name="name", property_type=PropertyType.STRING)
        prop_def2 = PropertyDefImpl(name="age", property_type=PropertyType.INTEGER)

        aspect_def = AspectDefImpl(
            name="person",
            properties={"name": prop_def1, "age": prop_def2},
        )

        aspect = AspectImpl(definition=aspect_def)
        aspect.set_property("name", "Alice")
        aspect.set_property("age", 30)

        json_bytes = CheapJsonSerializer.to_json(aspect)
        data = orjson.loads(json_bytes)

        assert data["aspectDefName"] == "person"
        assert data["properties"]["name"] == "Alice"
        assert data["properties"]["age"] == 30

    def test_serialize_aspect_with_null_values(self) -> None:
        """Test that null property values are excluded from serialization."""
        prop_def1 = PropertyDefImpl(name="name", property_type=PropertyType.STRING)
        prop_def2 = PropertyDefImpl(
            name="age", property_type=PropertyType.INTEGER, is_nullable=True
        )

        aspect_def = AspectDefImpl(
            name="person",
            properties={"name": prop_def1, "age": prop_def2},
        )

        aspect = AspectImpl(definition=aspect_def)
        aspect.set_property("name", "Bob")
        # age is not set (null)

        json_bytes = CheapJsonSerializer.to_json(aspect)
        data = orjson.loads(json_bytes)

        assert "name" in data["properties"]
        assert "age" not in data["properties"]  # Null values excluded


class TestEntitySerialization:
    """Test Entity serialization and deserialization."""

    def test_serialize_entity(self) -> None:
        """Test serializing an Entity."""
        entity_id = uuid4()
        entity = EntityImpl(id=entity_id)

        # Add an aspect
        prop_def = PropertyDefImpl(name="title", property_type=PropertyType.STRING)
        aspect_def = AspectDefImpl(name="book", properties={"title": prop_def})
        aspect = AspectImpl(definition=aspect_def)
        aspect.set_property("title", "1984")

        entity.add_aspect("book", aspect)

        json_bytes = CheapJsonSerializer.to_json(entity)
        data = orjson.loads(json_bytes)

        assert data["id"] == str(entity_id)
        assert "aspects" in data
        assert "book" in data["aspects"]
        assert data["aspects"]["book"]["properties"]["title"] == "1984"


class TestHierarchyDefSerialization:
    """Test HierarchyDef serialization."""

    def test_serialize_hierarchy_def(self) -> None:
        """Test serializing a HierarchyDef."""
        hierarchy_def = HierarchyDefImpl(
            name="documents",
            hierarchy_type=HierarchyType.ENTITY_LIST,
        )

        json_bytes = CheapJsonSerializer.to_json(hierarchy_def)
        data = orjson.loads(json_bytes)

        assert data["name"] == "documents"
        assert data["type"] == "ENTITY_LIST"

    def test_roundtrip_hierarchy_def(self) -> None:
        """Test HierarchyDef roundtrip serialization."""
        original = HierarchyDefImpl(
            name="users",
            hierarchy_type=HierarchyType.ENTITY_SET,
        )

        # Serialize
        json_bytes = CheapJsonSerializer.to_json(original)

        # Deserialize
        deserialized = CheapJsonDeserializer.from_json_hierarchy_def(json_bytes)

        assert deserialized.name == original.name
        assert deserialized.hierarchy_type == original.hierarchy_type


class TestCatalogDefSerialization:
    """Test CatalogDef serialization."""

    def test_serialize_catalog_def(self) -> None:
        """Test serializing a CatalogDef."""
        prop_def = PropertyDefImpl(name="name", property_type=PropertyType.STRING)
        aspect_def = AspectDefImpl(name="person", properties={"name": prop_def})
        hierarchy_def = HierarchyDefImpl(name="people", hierarchy_type=HierarchyType.ENTITY_LIST)

        catalog_def = CatalogDefImpl(
            aspect_defs={"person": aspect_def},
            hierarchy_defs={"people": hierarchy_def},
        )

        json_bytes = CheapJsonSerializer.to_json(catalog_def)
        data = orjson.loads(json_bytes)

        assert "aspectDefs" in data
        assert "person" in data["aspectDefs"]
        assert "hierarchyDefs" in data
        assert "people" in data["hierarchyDefs"]

    def test_roundtrip_catalog_def(self) -> None:
        """Test CatalogDef roundtrip serialization."""
        prop_def = PropertyDefImpl(name="email", property_type=PropertyType.STRING)
        aspect_def = AspectDefImpl(name="user", properties={"email": prop_def})

        original = CatalogDefImpl(aspect_defs={"user": aspect_def})

        # Serialize
        json_bytes = CheapJsonSerializer.to_json(original)

        # Deserialize
        deserialized = CheapJsonDeserializer.from_json_catalog_def(json_bytes)

        assert len(deserialized.aspect_defs) == 1
        assert "user" in deserialized.aspect_defs


class TestCatalogSerialization:
    """Test Catalog serialization."""

    def test_serialize_catalog(self) -> None:
        """Test serializing a Catalog."""
        catalog = CatalogImpl(
            species=CatalogSpecies.GIT,
            version="1.0.0",
        )

        prop_def = PropertyDefImpl(name="name", property_type=PropertyType.STRING)
        aspect_def = AspectDefImpl(name="item", properties={"name": prop_def})
        catalog.add_aspect_def(aspect_def)

        json_bytes = CheapJsonSerializer.to_json(catalog)
        data = orjson.loads(json_bytes)

        assert "id" in data
        assert data["species"] == "GIT"
        assert data["version"] == "1.0.0"
        assert "aspectDefs" in data
        assert "item" in data["aspectDefs"]


class TestPrettyPrinting:
    """Test pretty-printed JSON output."""

    def test_pretty_print(self) -> None:
        """Test that pretty=True produces formatted JSON."""
        prop_def = PropertyDefImpl(name="name", property_type=PropertyType.STRING)

        # Regular output
        json_regular = CheapJsonSerializer.to_json_str(prop_def, pretty=False)

        # Pretty output
        json_pretty = CheapJsonSerializer.to_json_str(prop_def, pretty=True)

        # Pretty output should have more characters (indentation)
        assert len(json_pretty) > len(json_regular)
        assert "\n" in json_pretty
        assert "  " in json_pretty  # Indentation


class TestUUIDSerialization:
    """Test UUID serialization."""

    def test_uuid_serialization(self) -> None:
        """Test that UUIDs are properly serialized as strings."""
        test_id = uuid4()
        aspect_def = AspectDefImpl(
            name="test",
            aspect_id=test_id,
            properties={},
        )

        json_bytes = CheapJsonSerializer.to_json(aspect_def)
        data = orjson.loads(json_bytes)

        # UUID should be serialized as string
        assert data["id"] == str(test_id)
        # Should be deserializable back to UUID
        assert UUID(data["id"]) == test_id
