"""Data Access Object for CHEAP catalog persistence in SQLite."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from cheap.core.property_type import PropertyType

if TYPE_CHECKING:
    import aiosqlite

    from cheap.core.aspect import Aspect, AspectDef
    from cheap.core.catalog import Catalog
    from cheap.core.entity import Entity
    from cheap.core.property import PropertyDef

    from cheap.db.sqlite.adapter import SqliteAdapter


# Property type mapping: PropertyType -> SQLite type abbreviation
PROPERTY_TYPE_TO_DB = {
    PropertyType.INTEGER: "INT",
    PropertyType.FLOAT: "FLT",
    PropertyType.BOOLEAN: "BLN",
    PropertyType.STRING: "STR",
    PropertyType.TEXT: "TXT",
    PropertyType.BIG_INTEGER: "BGI",
    PropertyType.BIG_DECIMAL: "BGF",
    PropertyType.DATE_TIME: "DAT",
    PropertyType.URI: "URI",
    PropertyType.UUID: "UID",
    PropertyType.CLOB: "CLB",
    PropertyType.BLOB: "BLB",
}

# Reverse mapping: SQLite type abbreviation -> PropertyType
DB_TO_PROPERTY_TYPE = {v: k for k, v in PROPERTY_TYPE_TO_DB.items()}


class SqliteDao:
    """
    Data Access Object for persisting CHEAP catalogs in SQLite.

    Provides methods to save and load complete catalog structures including:
    - Catalog metadata
    - Aspect definitions
    - Hierarchy definitions
    - Entities with aspects and properties
    - Hierarchy content

    All operations are wrapped in transactions for consistency.
    """

    def __init__(self, adapter: SqliteAdapter) -> None:
        """
        Initialize DAO with a database adapter.

        Args:
            adapter: Connected SqliteAdapter instance.
        """
        self._adapter = adapter

    async def save_catalog(self, catalog: Catalog) -> None:
        """
        Save a complete catalog to the database.

        This saves:
        - Catalog metadata
        - All aspect definitions
        - All hierarchy definitions
        - All entities with their aspects

        Args:
            catalog: Catalog to save.

        Raises:
            aiosqlite.Error: If save operation fails.
        """
        conn = await self._adapter.get_connection()

        try:
            # Save catalog metadata
            await self._save_catalog_metadata(conn, catalog)

            # Save aspect definitions
            aspect_defs = getattr(catalog, "_aspect_defs", {})
            for aspect_def in aspect_defs.values():
                await self._save_aspect_def(conn, catalog, aspect_def)

            # Save hierarchy definitions
            hierarchy_defs = getattr(catalog, "_hierarchy_defs", {})
            for hierarchy_def in hierarchy_defs.values():
                await self._save_hierarchy_def(conn, catalog, hierarchy_def)

            # Save entities (implementation would iterate through catalog entities)
            # Note: This requires access to catalog's entities, which may be in hierarchies

            await conn.commit()
        except Exception:
            await conn.rollback()
            raise

    async def load_catalog(self, catalog_id: UUID) -> Catalog:
        """
        Load a complete catalog from the database.

        Args:
            catalog_id: UUID of catalog to load.

        Returns:
            Loaded Catalog instance.

        Raises:
            ValueError: If catalog not found.
            aiosqlite.Error: If load operation fails.
        """
        from cheap.core.catalog_impl import CatalogImpl
        from cheap.core.catalog_species import CatalogSpecies

        conn = await self._adapter.get_connection()

        # Load catalog metadata
        cursor = await conn.execute(
            "SELECT id, species, version FROM catalog WHERE id = ?",
            (str(catalog_id),),
        )
        row = await cursor.fetchone()
        await cursor.close()

        if row is None:
            raise ValueError(f"Catalog not found: {catalog_id}")

        catalog = CatalogImpl(
            global_id=UUID(row[0]),
            species=CatalogSpecies(row[1]),
            version=row[2],
        )

        # Load aspect definitions
        await self._load_aspect_defs(conn, catalog)

        # Load hierarchy definitions
        await self._load_hierarchy_defs(conn, catalog)

        # Load entities and hierarchies
        # (Implementation would load all entities and populate hierarchies)

        return catalog

    async def delete_catalog(self, catalog_id: UUID) -> None:
        """
        Delete a catalog and all its data from the database.

        Args:
            catalog_id: UUID of catalog to delete.

        Raises:
            aiosqlite.Error: If delete operation fails.
        """
        conn = await self._adapter.get_connection()

        try:
            await conn.execute("DELETE FROM catalog WHERE id = ?", (str(catalog_id),))
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise

    # Private helper methods

    async def _save_catalog_metadata(self, conn: aiosqlite.Connection, catalog: Catalog) -> None:
        """Save catalog metadata to database."""
        catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))

        await conn.execute(
            """
            INSERT OR REPLACE INTO catalog (id, species, version)
            VALUES (?, ?, ?)
            """,
            (str(catalog_id), catalog.species.value, catalog.version),
        )

    async def _save_aspect_def(
        self,
        conn: aiosqlite.Connection,
        catalog: Catalog,
        aspect_def: AspectDef,
    ) -> None:
        """Save an aspect definition to database."""
        # Save aspect_def record
        await conn.execute(
            """
            INSERT OR REPLACE INTO aspect_def
            (id, name, is_readable, is_writable, can_add_properties, can_remove_properties)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(aspect_def.id),
                aspect_def.name,
                1 if aspect_def.is_readable else 0,
                1 if aspect_def.is_writable else 0,
                1 if aspect_def.can_add_properties else 0,
                1 if aspect_def.can_remove_properties else 0,
            ),
        )

        # Link to catalog
        catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))
        await conn.execute(
            """
            INSERT OR IGNORE INTO catalog_aspect_def (catalog_id, aspect_def_id)
            VALUES (?, ?)
            """,
            (str(catalog_id), str(aspect_def.id)),
        )

        # Save property definitions
        for prop_def in aspect_def.properties.values():
            await self._save_property_def(conn, aspect_def, prop_def)

    async def _save_property_def(
        self,
        conn: aiosqlite.Connection,
        aspect_def: AspectDef,
        prop_def: PropertyDef,
    ) -> None:
        """Save a property definition to database."""
        db_type = PROPERTY_TYPE_TO_DB[prop_def.property_type]

        await conn.execute(
            """
            INSERT OR REPLACE INTO property_def
            (aspect_def_id, name, type, is_writable, is_nullable, is_multivalued, default_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(aspect_def.id),
                prop_def.name,
                db_type,
                1 if prop_def.is_writable else 0,
                1 if prop_def.is_nullable else 0,
                1 if prop_def.is_multivalued else 0,
                str(prop_def.default_value) if prop_def.default_value is not None else None,
            ),
        )

    async def _save_hierarchy_def(
        self,
        conn: aiosqlite.Connection,
        catalog: Catalog,
        hierarchy_def: Any,  # HierarchyDef type
    ) -> None:
        """Save a hierarchy definition to database."""
        from cheap.core.hierarchy_type import HierarchyType

        catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))

        # Map HierarchyType to DB abbreviation
        type_map = {
            HierarchyType.ENTITY_LIST: "EL",
            HierarchyType.ENTITY_SET: "ES",
            HierarchyType.ENTITY_DIR: "ED",
            HierarchyType.ENTITY_TREE: "ET",
            HierarchyType.ASPECT_MAP: "AM",
        }

        db_type = type_map[hierarchy_def.hierarchy_type]

        await conn.execute(
            """
            INSERT OR REPLACE INTO hierarchy_def (catalog_id, name, type)
            VALUES (?, ?, ?)
            """,
            (str(catalog_id), hierarchy_def.name, db_type),
        )

    async def _save_entity(
        self, conn: aiosqlite.Connection, catalog: Catalog, entity: Entity
    ) -> None:
        """Save an entity and its aspects to database."""
        catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))

        # Save entity record
        await conn.execute(
            """
            INSERT OR REPLACE INTO entity (id, catalog_id)
            VALUES (?, ?)
            """,
            (str(entity.id), str(catalog_id)),
        )

        # Save aspects
        for aspect in entity.aspects.values():
            await self._save_aspect(conn, entity, aspect)

    async def _save_aspect(
        self, conn: aiosqlite.Connection, entity: Entity, aspect: Aspect
    ) -> None:
        """Save an aspect and its property values to database."""
        # Save aspect record
        cursor = await conn.execute(
            """
            INSERT INTO aspect (entity_id, aspect_def_id)
            VALUES (?, ?)
            RETURNING id
            """,
            (str(entity.id), str(aspect.definition.id)),
        )
        row = await cursor.fetchone()
        if row is None:
            raise ValueError(f"Failed to insert aspect for entity {entity.id}")
        aspect_id = row[0]
        await cursor.close()

        # Save property values
        aspect_def_id = str(aspect.definition.id)
        for prop_name, prop_def in aspect.definition.properties.items():
            prop = aspect.get_property(prop_name)
            if prop is not None and prop.value is not None:
                await self._save_property_value(
                    conn, aspect_id, aspect_def_id, prop_def, prop.value
                )

    async def _save_property_value(
        self,
        conn: aiosqlite.Connection,
        aspect_id: int,
        aspect_def_id: str,
        prop_def: PropertyDef,
        value: Any,
    ) -> None:
        """Save a property value to database."""
        # Get property_def id from database
        cursor = await conn.execute(
            """
            SELECT id FROM property_def
            WHERE aspect_def_id = ? AND name = ?
            """,
            (aspect_def_id, prop_def.name),
        )
        row = await cursor.fetchone()
        await cursor.close()

        if row is None:
            raise ValueError(f"Property definition not found: {prop_def.name}")

        property_def_id = row[0]

        # Determine how to store the value
        if prop_def.property_type == PropertyType.BLOB:
            # Store as binary
            value_text = None
            value_binary = value if isinstance(value, bytes) else str(value).encode()
        else:
            # Store as text (convert to string)
            value_text = str(value)
            value_binary = None

        await conn.execute(
            """
            INSERT INTO property_value (aspect_id, property_def_id, value_text, value_binary)
            VALUES (?, ?, ?, ?)
            """,
            (aspect_id, property_def_id, value_text, value_binary),
        )

    async def _load_aspect_defs(self, conn: aiosqlite.Connection, catalog: Catalog) -> None:
        """Load aspect definitions for a catalog."""
        from cheap.core.aspect_impl import AspectDefImpl
        from cheap.core.property_impl import PropertyDefImpl

        catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))

        # Load aspect defs linked to this catalog
        cursor = await conn.execute(
            """
            SELECT ad.id, ad.name, ad.is_readable, ad.is_writable,
                   ad.can_add_properties, ad.can_remove_properties
            FROM aspect_def ad
            JOIN catalog_aspect_def cad ON ad.id = cad.aspect_def_id
            WHERE cad.catalog_id = ?
            """,
            (str(catalog_id),),
        )

        rows = await cursor.fetchall()
        await cursor.close()

        for row in rows:
            aspect_def_id = UUID(row[0])
            aspect_name = row[1]

            # Load property definitions for this aspect
            prop_cursor = await conn.execute(
                """
                SELECT name, type, is_writable, is_nullable, is_multivalued, default_value
                FROM property_def
                WHERE aspect_def_id = ?
                """,
                (str(aspect_def_id),),
            )

            prop_rows = await prop_cursor.fetchall()
            await prop_cursor.close()

            properties = {}
            for prop_row in prop_rows:
                prop_type = DB_TO_PROPERTY_TYPE[prop_row[1]]
                prop_def = PropertyDefImpl(
                    name=prop_row[0],
                    property_type=prop_type,
                    is_writable=bool(prop_row[2]),
                    is_nullable=bool(prop_row[3]),
                    is_multivalued=bool(prop_row[4]),
                    default_value=prop_row[5],
                )
                properties[prop_def.name] = prop_def

            # Create aspect definition
            aspect_def = AspectDefImpl(
                id=aspect_def_id,
                name=aspect_name,
                properties=properties,
                is_readable=bool(row[2]),
                is_writable=bool(row[3]),
                can_add_properties=bool(row[4]),
                can_remove_properties=bool(row[5]),
            )

            catalog.add_aspect_def(aspect_def)

    async def _load_hierarchy_defs(self, conn: aiosqlite.Connection, catalog: Catalog) -> None:
        """Load hierarchy definitions for a catalog."""
        #  TODO: Implement hierarchy definition loading when hierarchy support is complete
        # Currently CatalogImpl tracks Hierarchy instances, not HierarchyDef
        # This will be implemented when full hierarchy persistence is added
        pass
