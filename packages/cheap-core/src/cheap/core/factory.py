"""Factory utilities for creating CHEAP objects."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from cheap.core.aspect_impl import AspectDefImpl, AspectImpl
from cheap.core.catalog_impl import CatalogDefImpl, CatalogImpl, HierarchyDefImpl
from cheap.core.entity_impl import EntityImpl
from cheap.core.hierarchy_impl import (
    AspectMapHierarchyImpl,
    EntityDirectoryHierarchyImpl,
    EntityListHierarchyImpl,
    EntitySetHierarchyImpl,
    EntityTreeHierarchyImpl,
    EntityTreeNodeImpl,
)
from cheap.core.property_impl import PropertyDefImpl, PropertyImpl

if TYPE_CHECKING:
    from cheap.core.aspect import Aspect, AspectDef
    from cheap.core.catalog import Catalog, CatalogDef, HierarchyDef
    from cheap.core.catalog_species import CatalogSpecies
    from cheap.core.entity import Entity
    from cheap.core.hierarchy import (
        AspectMapHierarchy,
        EntityDirectoryHierarchy,
        EntityListHierarchy,
        EntitySetHierarchy,
        EntityTreeHierarchy,
        EntityTreeNode,
    )
    from cheap.core.hierarchy_type import HierarchyType
    from cheap.core.property import Property, PropertyDef
    from cheap.core.property_type import PropertyType, PropertyValue


class CheapFactory:
    """
    Factory class for creating CHEAP objects.

    Provides convenient factory methods for creating entities, aspects,
    properties, hierarchies, and catalogs with default configurations.
    """

    # Property creation

    @staticmethod
    def create_property_def(
        name: str,
        property_type: PropertyType,
        *,
        default_value: PropertyValue = None,
        has_default_value: bool = False,
        is_readable: bool = True,
        is_writable: bool = True,
        is_nullable: bool = True,
        is_multivalued: bool = False,
    ) -> PropertyDef:
        """
        Create a new property definition.

        Args:
            name: Property name.
            property_type: Type of the property.
            default_value: Default value for the property.
            has_default_value: Whether a default value is set.
            is_readable: Whether the property can be read.
            is_writable: Whether the property can be written.
            is_nullable: Whether the property can be null.
            is_multivalued: Whether the property can have multiple values.

        Returns:
            A new PropertyDef instance.
        """
        return PropertyDefImpl(
            name=name,
            property_type=property_type,
            default_value=default_value,
            has_default_value=has_default_value,
            is_readable=is_readable,
            is_writable=is_writable,
            is_nullable=is_nullable,
            is_multivalued=is_multivalued,
        )

    @staticmethod
    def create_property(definition: PropertyDef, value: PropertyValue = None) -> Property:
        """
        Create a new property with a definition and optional value.

        Args:
            definition: The property definition.
            value: Initial value for the property.

        Returns:
            A new Property instance.
        """
        prop = PropertyImpl(definition=definition)
        if value is not None:
            prop.value = value
        return prop

    # Aspect creation

    @staticmethod
    def create_aspect_def(
        name: str,
        properties: dict[str, PropertyDef] | None = None,
        *,
        aspect_id: UUID | None = None,
        is_readable: bool = True,
        is_writable: bool = True,
        can_add_properties: bool = False,
        can_remove_properties: bool = False,
    ) -> AspectDef:
        """
        Create a new aspect definition.

        Args:
            name: Aspect name.
            properties: Dictionary of property definitions.
            aspect_id: Unique ID for the aspect (auto-generated if not provided).
            is_readable: Whether the aspect can be read.
            is_writable: Whether the aspect can be written.
            can_add_properties: Whether properties can be added dynamically.
            can_remove_properties: Whether properties can be removed dynamically.

        Returns:
            A new AspectDef instance.
        """
        return AspectDefImpl(
            name=name,
            properties=properties or {},
            id=aspect_id or uuid4(),
            is_readable=is_readable,
            is_writable=is_writable,
            can_add_properties=can_add_properties,
            can_remove_properties=can_remove_properties,
        )

    @staticmethod
    def create_aspect(definition: AspectDef, entity: Entity | None = None) -> Aspect:
        """
        Create a new aspect with a definition.

        Args:
            definition: The aspect definition.
            entity: Optional entity to associate with the aspect.

        Returns:
            A new Aspect instance.
        """
        return AspectImpl(definition=definition, entity=entity)

    # Entity creation

    @staticmethod
    def create_entity(entity_id: UUID | None = None) -> Entity:
        """
        Create a new entity.

        Args:
            entity_id: Unique ID for the entity (auto-generated if not provided).

        Returns:
            A new Entity instance.
        """
        return EntityImpl(id=entity_id or uuid4())

    # Hierarchy creation

    @staticmethod
    def create_entity_list_hierarchy(name: str) -> EntityListHierarchy:
        """
        Create a new entity list hierarchy.

        Args:
            name: Hierarchy name.

        Returns:
            A new EntityListHierarchy instance.
        """
        return EntityListHierarchyImpl(name=name)

    @staticmethod
    def create_entity_set_hierarchy(name: str) -> EntitySetHierarchy:
        """
        Create a new entity set hierarchy.

        Args:
            name: Hierarchy name.

        Returns:
            A new EntitySetHierarchy instance.
        """
        return EntitySetHierarchyImpl(name=name)

    @staticmethod
    def create_entity_directory_hierarchy(name: str) -> EntityDirectoryHierarchy:
        """
        Create a new entity directory hierarchy.

        Args:
            name: Hierarchy name.

        Returns:
            A new EntityDirectoryHierarchy instance.
        """
        return EntityDirectoryHierarchyImpl(name=name)

    @staticmethod
    def create_entity_tree_hierarchy(name: str) -> EntityTreeHierarchy:
        """
        Create a new entity tree hierarchy.

        Args:
            name: Hierarchy name.

        Returns:
            A new EntityTreeHierarchy instance.
        """
        return EntityTreeHierarchyImpl(name=name)

    @staticmethod
    def create_aspect_map_hierarchy(name: str) -> AspectMapHierarchy:
        """
        Create a new aspect map hierarchy.

        Args:
            name: Hierarchy name.

        Returns:
            A new AspectMapHierarchy instance.
        """
        return AspectMapHierarchyImpl(name=name)

    @staticmethod
    def create_tree_node(entity_id: UUID) -> EntityTreeNode:
        """
        Create a new tree node for an entity.

        Args:
            entity_id: ID of the entity this node represents.

        Returns:
            A new EntityTreeNode instance.
        """
        return EntityTreeNodeImpl(entity_id=entity_id)

    # Catalog creation

    @staticmethod
    def create_hierarchy_def(name: str, hierarchy_type: HierarchyType) -> HierarchyDef:
        """
        Create a new hierarchy definition.

        Args:
            name: Hierarchy name.
            hierarchy_type: Type of hierarchy.

        Returns:
            A new HierarchyDef instance.
        """
        return HierarchyDefImpl(name=name, hierarchy_type=hierarchy_type)

    @staticmethod
    def create_catalog_def() -> CatalogDef:
        """
        Create a new catalog definition.

        Returns:
            A new CatalogDef instance.
        """
        return CatalogDefImpl()

    @staticmethod
    def create_catalog(species: CatalogSpecies, version: str = "1.0.0") -> Catalog:
        """
        Create a new catalog.

        Args:
            species: Type/species of catalog.
            version: Catalog version string.

        Returns:
            A new Catalog instance.
        """
        return CatalogImpl(species=species, version=version)
