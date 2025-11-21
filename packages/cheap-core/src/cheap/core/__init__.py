"""
Cheap Core Module.

This module provides the core interfaces and basic implementations for the CHEAP
model (Catalog, Hierarchy, Entity, Aspect, Property) - a git-like system for
structured data.
"""

# Enums
# Core protocols
from cheap.core.aspect import Aspect, AspectDef
from cheap.core.catalog import Catalog, CatalogDef, HierarchyDef
from cheap.core.catalog_species import CatalogSpecies, CatalogSpeciesLiteral
from cheap.core.entity import Entity
from cheap.core.hierarchy import (
    AspectMapHierarchy,
    EntityDirectoryHierarchy,
    EntityListHierarchy,
    EntitySetHierarchy,
    EntityTreeHierarchy,
    Hierarchy,
    Node,
)
from cheap.core.hierarchy_type import HierarchyType, HierarchyTypeLiteral
from cheap.core.property import Property, PropertyDef
from cheap.core.property_type import PropertyType, PropertyTypeLiteral, PropertyValue

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
    "Node",
    "EntityListHierarchy",
    "EntitySetHierarchy",
    "EntityDirectoryHierarchy",
    "EntityTreeHierarchy",
    "AspectMapHierarchy",
]
