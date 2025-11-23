"""Core deserialization module for CHEAP objects using orjson."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import orjson
from cheap.core.aspect_impl import AspectDefImpl, AspectImpl
from cheap.core.catalog_impl import CatalogDefImpl, CatalogImpl, HierarchyDefImpl
from cheap.core.entity_impl import EntityImpl
from cheap.core.property_impl import PropertyDefImpl, PropertyImpl
from cheap.core.property_type import PropertyType

if TYPE_CHECKING:
    from cheap.core.aspect import Aspect, AspectDef
    from cheap.core.catalog import Catalog, CatalogDef, HierarchyDef
    from cheap.core.entity import Entity
    from cheap.core.property import Property, PropertyDef


class CheapJsonDeserializer:
    """
    Main deserialization class for CHEAP data model objects.

    Provides methods to deserialize JSON to CHEAP objects using orjson.
    """

    @staticmethod
    def from_json_property_def(json_data: bytes | str) -> PropertyDef:
        """
        Deserialize JSON to a PropertyDef object.

        Args:
            json_data: JSON bytes or string.

        Returns:
            PropertyDef object.
        """
        data = _load_json(json_data)
        return _deserialize_property_def(data)

    @staticmethod
    def from_json_aspect_def(json_data: bytes | str) -> AspectDef:
        """
        Deserialize JSON to an AspectDef object.

        Args:
            json_data: JSON bytes or string.

        Returns:
            AspectDef object.
        """
        data = _load_json(json_data)
        return _deserialize_aspect_def(data)

    @staticmethod
    def from_json_aspect(json_data: bytes | str, aspect_def: AspectDef) -> Aspect:
        """
        Deserialize JSON to an Aspect object.

        Args:
            json_data: JSON bytes or string.
            aspect_def: The AspectDef for this aspect.

        Returns:
            Aspect object.
        """
        data = _load_json(json_data)
        return _deserialize_aspect(data, aspect_def)

    @staticmethod
    def from_json_entity(json_data: bytes | str) -> Entity:
        """
        Deserialize JSON to an Entity object.

        Args:
            json_data: JSON bytes or string.

        Returns:
            Entity object.
        """
        data = _load_json(json_data)
        return _deserialize_entity(data)

    @staticmethod
    def from_json_hierarchy_def(json_data: bytes | str) -> HierarchyDef:
        """
        Deserialize JSON to a HierarchyDef object.

        Args:
            json_data: JSON bytes or string.

        Returns:
            HierarchyDef object.
        """
        data = _load_json(json_data)
        return _deserialize_hierarchy_def(data)

    @staticmethod
    def from_json_catalog_def(json_data: bytes | str) -> CatalogDef:
        """
        Deserialize JSON to a CatalogDef object.

        Args:
            json_data: JSON bytes or string.

        Returns:
            CatalogDef object.
        """
        data = _load_json(json_data)
        return _deserialize_catalog_def(data)

    @staticmethod
    def from_json_catalog(json_data: bytes | str) -> Catalog:
        """
        Deserialize JSON to a Catalog object.

        Args:
            json_data: JSON bytes or string.

        Returns:
            Catalog object.
        """
        data = _load_json(json_data)
        return _deserialize_catalog(data)


def _load_json(json_data: bytes | str) -> dict[str, Any]:
    """
    Load JSON data into a dictionary.

    Args:
        json_data: JSON as bytes or string.

    Returns:
        Parsed JSON dictionary.
    """
    if isinstance(json_data, str):
        json_data = json_data.encode("utf-8")
    return orjson.loads(json_data)


def _deserialize_property_def(data: dict[str, Any]) -> PropertyDef:
    """Deserialize a PropertyDef from dictionary."""
    property_type = PropertyType(data["type"])

    return PropertyDefImpl(
        name=data["name"],
        property_type=property_type,
        is_writable=data.get("isWritable", True),
        is_nullable=data.get("isNullable", True),
        is_multivalued=data.get("isMultivalued", False),
        default_value=data.get("defaultValue"),
    )


def _deserialize_property(data: dict[str, Any], prop_def: PropertyDef) -> Property:
    """Deserialize a Property from dictionary."""
    prop = PropertyImpl(definition=prop_def)
    if "value" in data:
        prop.value = data["value"]
    return prop


def _deserialize_aspect_def(data: dict[str, Any]) -> AspectDef:
    """Deserialize an AspectDef from dictionary."""
    aspect_id = UUID(data["id"]) if "id" in data else None

    properties: dict[str, PropertyDef] = {}
    if "properties" in data:
        for prop_name, prop_data in data["properties"].items():
            properties[prop_name] = _deserialize_property_def(prop_data)

    return AspectDefImpl(
        name=data["name"],
        id=aspect_id or uuid4(),
        properties=properties,
        can_add_properties=data.get("canAddProperties", False),
        can_remove_properties=data.get("canRemoveProperties", False),
    )


def _deserialize_aspect(data: dict[str, Any], aspect_def: AspectDef) -> Aspect:
    """Deserialize an Aspect from dictionary."""
    aspect = AspectImpl(definition=aspect_def)

    if "properties" in data:
        for prop_name, prop_value in data["properties"].items():
            if prop_name in aspect_def.properties:
                aspect.set_property(prop_name, prop_value)

    return aspect


def _deserialize_entity(data: dict[str, Any]) -> Entity:
    """Deserialize an Entity from dictionary."""
    entity_id = UUID(data["id"])
    entity = EntityImpl(id=entity_id)

    # Note: Deserializing aspects requires AspectDef context
    # This is a simplified version
    if "aspects" in data:
        # We would need access to AspectDefs to fully deserialize aspects
        pass

    return entity


def _deserialize_hierarchy_def(data: dict[str, Any]) -> HierarchyDef:
    """Deserialize a HierarchyDef from dictionary."""
    from cheap.core.hierarchy_type import HierarchyType

    hierarchy_type = HierarchyType(data["type"])

    return HierarchyDefImpl(
        name=data["name"],
        hierarchy_type=hierarchy_type,
    )


def _deserialize_catalog_def(data: dict[str, Any]) -> CatalogDef:
    """Deserialize a CatalogDef from dictionary."""
    aspect_defs: dict[str, AspectDef] = {}
    if "aspectDefs" in data:
        for aspect_name, aspect_data in data["aspectDefs"].items():
            aspect_defs[aspect_name] = _deserialize_aspect_def(aspect_data)

    hierarchy_defs: dict[str, HierarchyDef] = {}
    if "hierarchyDefs" in data:
        for hierarchy_name, hierarchy_data in data["hierarchyDefs"].items():
            hierarchy_defs[hierarchy_name] = _deserialize_hierarchy_def(hierarchy_data)

    return CatalogDefImpl(
        aspect_defs=aspect_defs,
        hierarchy_defs=hierarchy_defs,
    )


def _deserialize_catalog(data: dict[str, Any]) -> Catalog:
    """Deserialize a Catalog from dictionary."""
    from cheap.core.catalog_species import CatalogSpecies

    global_id = UUID(data["id"])
    species = CatalogSpecies(data["species"])
    version = data.get("version", "1.0.0")

    catalog = CatalogImpl(
        global_id=global_id,
        species=species,
        version=version,
    )

    # Deserialize aspect definitions
    if "aspectDefs" in data:
        for _aspect_name, aspect_data in data["aspectDefs"].items():
            aspect_def = _deserialize_aspect_def(aspect_data)
            catalog.add_aspect_def(aspect_def)

    # Deserialize hierarchies (simplified)
    # Full hierarchy deserialization would require more context

    return catalog
