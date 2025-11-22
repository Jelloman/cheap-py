"""
Cheap Core Module.

This module provides the core interfaces and basic implementations for the CHEAP
model (Catalog, Hierarchy, Entity, Aspect, Property) - a git-like system for
structured data.
"""

# Enums
from cheap.core.catalog_species import CatalogSpecies, CatalogSpeciesLiteral
from cheap.core.hierarchy_type import HierarchyType, HierarchyTypeLiteral
from cheap.core.property_type import PropertyType, PropertyTypeLiteral, PropertyValue

# Core protocols
from cheap.core.aspect import Aspect, AspectDef
from cheap.core.catalog import Catalog, CatalogDef, HierarchyDef
from cheap.core.entity import Entity
from cheap.core.hierarchy import (
    AspectMapHierarchy,
    EntityDirectoryHierarchy,
    EntityListHierarchy,
    EntitySetHierarchy,
    EntityTreeHierarchy,
    EntityTreeNode,
    Hierarchy,
)
from cheap.core.property import Property, PropertyDef

# Basic implementations
from cheap.core.aspect_impl import AspectDefImpl, AspectImpl
from cheap.core.catalog_impl import CatalogDefImpl, CatalogImpl, HierarchyDefImpl
from cheap.core.entity_impl import EntityImpl
from cheap.core.hierarchy_impl import (
    AspectMapHierarchyImpl,
    EntityDirectoryHierarchyImpl,
    EntityListHierarchyImpl,
    EntitySetHierarchyImpl,
    EntityTreeHierarchyImpl,
    NodeImpl,
)
from cheap.core.property_impl import PropertyDefImpl, PropertyImpl

__all__ = [
    # Enums
    "PropertyType",
    "PropertyTypeLiteral",
    "PropertyValue",
    "HierarchyType",
    "HierarchyTypeLiteral",
    "CatalogSpecies",
    "CatalogSpeciesLiteral",
    # Property protocols
    "Property",
    "PropertyDef",
    # Aspect protocols
    "Aspect",
    "AspectDef",
    # Entity protocol
    "Entity",
    # Catalog protocols
    "Catalog",
    "CatalogDef",
    "HierarchyDef",
    # Hierarchy protocols
    "Hierarchy",
    "EntityTreeNode",
    "EntityListHierarchy",
    "EntitySetHierarchy",
    "EntityDirectoryHierarchy",
    "EntityTreeHierarchy",
    "AspectMapHierarchy",
    # Property implementations
    "PropertyDefImpl",
    "PropertyImpl",
    # Aspect implementations
    "AspectDefImpl",
    "AspectImpl",
    # Entity implementations
    "EntityImpl",
    # Catalog implementations
    "CatalogDefImpl",
    "CatalogImpl",
    "HierarchyDefImpl",
    # Hierarchy implementations
    "EntityListHierarchyImpl",
    "EntitySetHierarchyImpl",
    "EntityDirectoryHierarchyImpl",
    "EntityTreeHierarchyImpl",
    "AspectMapHierarchyImpl",
    "NodeImpl",
]
