"""Core serialization module for CHEAP objects using orjson."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import orjson

if TYPE_CHECKING:
    from cheap.core.aspect import Aspect, AspectDef
    from cheap.core.catalog import Catalog, CatalogDef, HierarchyDef
    from cheap.core.entity import Entity
    from cheap.core.hierarchy import Hierarchy
    from cheap.core.property import Property, PropertyDef


def _default_encoder(obj: Any) -> Any:
    """
    Custom encoder for types not natively supported by orjson.

    orjson natively handles: UUID, datetime, date, time, bytes
    This function handles additional CHEAP-specific types.

    Args:
        obj: Object to encode.

    Returns:
        JSON-serializable representation.

    Raises:
        TypeError: If the object type cannot be serialized.
    """
    # orjson already handles UUID, datetime, bytes automatically
    # We just need to handle our custom types by converting them to dicts
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class CheapJsonSerializer:
    """
    Main serialization class for CHEAP data model objects.

    Provides methods to serialize CHEAP objects (Catalog, Aspect, Property, etc.)
    to JSON format using orjson for high performance.

    Uses orjson features:
    - Native UUID support
    - Native datetime support
    - Fast serialization (2-5x faster than standard json)
    - Deterministic output with OPT_SORT_KEYS
    """

    @staticmethod
    def to_json(
        obj: Catalog
        | CatalogDef
        | AspectDef
        | PropertyDef
        | HierarchyDef
        | Aspect
        | Property
        | Entity
        | Hierarchy,
        *,
        pretty: bool = False,
    ) -> bytes:
        """
        Serialize a CHEAP object to JSON bytes.

        Args:
            obj: The CHEAP object to serialize.
            pretty: If True, format JSON with indentation for readability.

        Returns:
            JSON as bytes (orjson returns bytes, not str).

        Raises:
            TypeError: If the object type is not supported.
        """
        options = orjson.OPT_SORT_KEYS | orjson.OPT_SERIALIZE_UUID

        if pretty:
            options |= orjson.OPT_INDENT_2

        # Dispatch to appropriate serializer based on type
        data = _serialize_object(obj)
        return orjson.dumps(data, option=options)

    @staticmethod
    def to_json_str(
        obj: Catalog
        | CatalogDef
        | AspectDef
        | PropertyDef
        | HierarchyDef
        | Aspect
        | Property
        | Entity
        | Hierarchy,
        *,
        pretty: bool = False,
    ) -> str:
        """
        Serialize a CHEAP object to JSON string.

        Args:
            obj: The CHEAP object to serialize.
            pretty: If True, format JSON with indentation for readability.

        Returns:
            JSON as a UTF-8 string.
        """
        return CheapJsonSerializer.to_json(obj, pretty=pretty).decode("utf-8")


def _serialize_object(obj: Any) -> dict[str, Any]:
    """
    Dispatch to appropriate serializer based on object type.

    Args:
        obj: Object to serialize.

    Returns:
        Dictionary representation ready for JSON serialization.

    Raises:
        TypeError: If object type is not supported.
    """
    from cheap.core.aspect import Aspect, AspectDef
    from cheap.core.catalog import Catalog, CatalogDef, HierarchyDef
    from cheap.core.entity import Entity
    from cheap.core.hierarchy import Hierarchy
    from cheap.core.property import Property, PropertyDef

    if isinstance(obj, PropertyDef):
        return _serialize_property_def(obj)
    elif isinstance(obj, Property):
        return _serialize_property(obj)
    elif isinstance(obj, AspectDef):
        return _serialize_aspect_def(obj)
    elif isinstance(obj, Aspect):
        return _serialize_aspect(obj)
    elif isinstance(obj, Entity):
        return _serialize_entity(obj)
    elif isinstance(obj, HierarchyDef):
        return _serialize_hierarchy_def(obj)
    elif isinstance(obj, Hierarchy):
        return _serialize_hierarchy(obj)
    elif isinstance(obj, CatalogDef):
        return _serialize_catalog_def(obj)
    elif isinstance(obj, Catalog):
        return _serialize_catalog(obj)
    else:
        raise TypeError(f"Unsupported type for serialization: {type(obj)}")


def _serialize_property_def(prop_def: PropertyDef) -> dict[str, Any]:
    """Serialize a PropertyDef to a dictionary."""
    result: dict[str, Any] = {
        "name": prop_def.name,
        "type": prop_def.property_type.value,
    }

    # Only include non-default values to keep JSON compact
    if not prop_def.is_writable:
        result["isWritable"] = False
    if prop_def.is_nullable:
        result["isNullable"] = True
    if prop_def.is_multivalued:
        result["isMultivalued"] = True
    if prop_def.default_value is not None:
        result["defaultValue"] = prop_def.default_value

    return result


def _serialize_property(prop: Property) -> dict[str, Any]:
    """Serialize a Property to a dictionary."""
    return {
        "def": _serialize_property_def(prop.definition),
        "value": prop.value,
    }


def _serialize_aspect_def(aspect_def: AspectDef) -> dict[str, Any]:
    """Serialize an AspectDef to a dictionary."""
    result: dict[str, Any] = {
        "name": aspect_def.name,
        "id": str(aspect_def.id),
        "properties": {
            name: _serialize_property_def(prop_def)
            for name, prop_def in aspect_def.properties.items()
        },
    }

    # Include optional fields
    if not aspect_def.can_add_properties:
        result["canAddProperties"] = False
    if not aspect_def.can_remove_properties:
        result["canRemoveProperties"] = False

    return result


def _serialize_aspect(aspect: Aspect, include_def_name: bool = True) -> dict[str, Any]:
    """Serialize an Aspect to a dictionary."""
    result: dict[str, Any] = {}

    if include_def_name:
        result["aspectDefName"] = aspect.definition.name

    # Serialize all properties
    properties: dict[str, Any] = {}
    for prop_name, _prop_def in aspect.definition.properties.items():
        prop = aspect.get_property(prop_name)
        if prop is not None and prop.value is not None:
            properties[prop_name] = prop.value

    if properties:
        result["properties"] = properties

    return result


def _serialize_entity(entity: Entity) -> dict[str, Any]:
    """Serialize an Entity to a dictionary."""
    return {
        "id": str(entity.id),
        "aspects": {
            name: _serialize_aspect(aspect, include_def_name=False)
            for name, aspect in entity.aspects.items()
        },
    }


def _serialize_hierarchy_def(hierarchy_def: HierarchyDef) -> dict[str, Any]:
    """Serialize a HierarchyDef to a dictionary."""
    return {
        "name": hierarchy_def.name,
        "type": hierarchy_def.hierarchy_type.value,
    }


def _serialize_hierarchy(hierarchy: Hierarchy) -> dict[str, Any]:
    """Serialize a Hierarchy to a dictionary."""
    from cheap.core.hierarchy import (
        AspectMapHierarchy,
        EntityDirectoryHierarchy,
        EntityListHierarchy,
        EntitySetHierarchy,
        EntityTreeHierarchy,
    )

    result: dict[str, Any] = {
        "name": hierarchy.definition.name,
        "type": hierarchy.definition.hierarchy_type.value,
    }

    # Type-specific serialization
    if isinstance(hierarchy, (EntityListHierarchy, EntitySetHierarchy)):
        result["entities"] = [str(eid) for eid in hierarchy.all_entities]
    elif isinstance(hierarchy, EntityDirectoryHierarchy):
        result["entries"] = {key: str(eid) for key, eid in hierarchy.items()}
    elif isinstance(hierarchy, EntityTreeHierarchy):
        # Serialize tree structure would go here
        result["nodes"] = {}  # Placeholder for tree serialization
    elif isinstance(hierarchy, AspectMapHierarchy):
        # Serialize aspect map would go here
        result["aspects"] = {}  # Placeholder for aspect map serialization

    return result


def _serialize_catalog_def(catalog_def: CatalogDef) -> dict[str, Any]:
    """Serialize a CatalogDef to a dictionary."""
    return {
        "aspectDefs": {
            name: _serialize_aspect_def(aspect_def)
            for name, aspect_def in catalog_def.aspect_defs.items()
        },
        "hierarchyDefs": {
            name: _serialize_hierarchy_def(hierarchy_def)
            for name, hierarchy_def in catalog_def.hierarchy_defs.items()
        },
    }


def _serialize_catalog(catalog: Catalog) -> dict[str, Any]:
    """Serialize a Catalog to a dictionary."""
    result: dict[str, Any] = {
        "id": str(catalog.id),
        "species": catalog.species.value,
        "version": catalog.version,
        "aspectDefs": {
            name: _serialize_aspect_def(aspect_def)
            for name, aspect_def in catalog.get_all_aspect_defs().items()
        },
        "hierarchies": {
            name: _serialize_hierarchy(hierarchy)
            for name, hierarchy in catalog.get_all_hierarchies().items()
        },
    }

    return result
