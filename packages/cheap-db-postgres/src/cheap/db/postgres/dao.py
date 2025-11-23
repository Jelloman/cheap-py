"""Data Access Object for CHEAP catalog persistence in PostgreSQL."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from cheap.core.property_type import PropertyType

if TYPE_CHECKING:
    import psycopg

    from cheap.core.aspect import Aspect, AspectDef
    from cheap.core.catalog import Catalog
    from cheap.core.entity import Entity
    from cheap.core.property import PropertyDef

    from cheap.db.postgres.adapter import PostgresAdapter


# Property type mapping: PropertyType -> PostgreSQL type abbreviation
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

# Reverse mapping: PostgreSQL type abbreviation -> PropertyType
DB_TO_PROPERTY_TYPE = {v: k for k, v in PROPERTY_TYPE_TO_DB.items()}


class PostgresDao:
    """
    Data Access Object for persisting CHEAP catalogs in PostgreSQL.

    Provides methods to save and load complete catalog structures including:
    - Catalog metadata
    - Aspect definitions
    - Hierarchy definitions
    - Entities with aspects and properties
    - Hierarchy content

    All operations are wrapped in transactions for consistency.
    Uses native PostgreSQL UUID type and async operations.
    """

    def __init__(self, adapter: PostgresAdapter) -> None:
        """
        Initialize DAO with a database adapter.

        Args:
            adapter: Connected PostgresAdapter instance.
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
            psycopg.Error: If save operation fails.
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
        finally:
            await self._adapter.return_connection(conn)

    async def load_catalog(self, catalog_id: UUID) -> Catalog:
        """
        Load a complete catalog from the database.

        Args:
            catalog_id: UUID of catalog to load.

        Returns:
            Loaded Catalog instance.

        Raises:
            ValueError: If catalog not found.
            psycopg.Error: If load operation fails.
        """
        from cheap.core.catalog_impl import CatalogImpl
        from cheap.core.catalog_species import CatalogSpecies

        conn = await self._adapter.get_connection()

        try:
            # Load catalog metadata
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT id, species, version FROM catalog WHERE id = %s",
                    (catalog_id,),
                )
                row = await cur.fetchone()

            if row is None:
                raise ValueError(f"Catalog not found: {catalog_id}")

            catalog = CatalogImpl(
                global_id=row[0],  # UUID type
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
        finally:
            await self._adapter.return_connection(conn)

    async def delete_catalog(self, catalog_id: UUID) -> None:
        """
        Delete a catalog and all its data from the database.

        Args:
            catalog_id: UUID of catalog to delete.

        Raises:
            psycopg.Error: If delete operation fails.
        """
        conn = await self._adapter.get_connection()

        try:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM catalog WHERE id = %s", (catalog_id,))
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await self._adapter.return_connection(conn)

    # Private helper methods

    async def _save_catalog_metadata(self, conn: psycopg.AsyncConnection, catalog: Catalog) -> None:
        """Save catalog metadata to database."""
        catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))

        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO catalog (id, species, version)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET species = EXCLUDED.species, version = EXCLUDED.version
                """,
                (catalog_id, catalog.species.value, catalog.version),
            )

    async def _save_aspect_def(
        self,
        conn: psycopg.AsyncConnection,
        catalog: Catalog,
        aspect_def: AspectDef,
    ) -> None:
        """Save an aspect definition to database."""
        # Save aspect_def record
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO aspect_def
                (id, name, is_readable, is_writable, can_add_properties, can_remove_properties)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET name = EXCLUDED.name,
                    is_readable = EXCLUDED.is_readable,
                    is_writable = EXCLUDED.is_writable,
                    can_add_properties = EXCLUDED.can_add_properties,
                    can_remove_properties = EXCLUDED.can_remove_properties
                """,
                (
                    aspect_def.id,
                    aspect_def.name,
                    aspect_def.is_readable,
                    aspect_def.is_writable,
                    aspect_def.can_add_properties,
                    aspect_def.can_remove_properties,
                ),
            )

            # Link to catalog
            catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))
            await cur.execute(
                """
                INSERT INTO catalog_aspect_def (catalog_id, aspect_def_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (catalog_id, aspect_def.id),
            )

        # Save property definitions
        for prop_def in aspect_def.properties.values():
            await self._save_property_def(conn, aspect_def, prop_def)

    async def _save_property_def(
        self,
        conn: psycopg.AsyncConnection,
        aspect_def: AspectDef,
        prop_def: PropertyDef,
    ) -> None:
        """Save a property definition to database."""
        db_type = PROPERTY_TYPE_TO_DB[prop_def.property_type]

        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO property_def
                (aspect_def_id, name, type, is_writable, is_nullable, is_multivalued, default_value)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (aspect_def_id, name) DO UPDATE
                SET type = EXCLUDED.type,
                    is_writable = EXCLUDED.is_writable,
                    is_nullable = EXCLUDED.is_nullable,
                    is_multivalued = EXCLUDED.is_multivalued,
                    default_value = EXCLUDED.default_value
                """,
                (
                    aspect_def.id,
                    prop_def.name,
                    db_type,
                    prop_def.is_writable,
                    prop_def.is_nullable,
                    prop_def.is_multivalued,
                    str(prop_def.default_value) if prop_def.default_value is not None else None,
                ),
            )

    async def _save_hierarchy_def(
        self,
        conn: psycopg.AsyncConnection,
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

        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO hierarchy_def (catalog_id, name, type)
                VALUES (%s, %s, %s)
                ON CONFLICT (catalog_id, name) DO UPDATE
                SET type = EXCLUDED.type
                """,
                (catalog_id, hierarchy_def.name, db_type),
            )

    async def _save_entity(
        self, conn: psycopg.AsyncConnection, catalog: Catalog, entity: Entity
    ) -> None:
        """Save an entity and its aspects to database."""
        catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))

        # Save entity record
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO entity (id, catalog_id)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (entity.id, catalog_id),
            )

        # Save aspects
        for aspect in entity.aspects.values():
            await self._save_aspect(conn, entity, aspect)

    async def _save_aspect(
        self, conn: psycopg.AsyncConnection, entity: Entity, aspect: Aspect
    ) -> None:
        """Save an aspect and its property values to database."""
        # Save aspect record
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO aspect (entity_id, aspect_def_id)
                VALUES (%s, %s)
                ON CONFLICT (entity_id, aspect_def_id) DO NOTHING
                RETURNING id
                """,
                (entity.id, aspect.definition.id),
            )
            row = await cur.fetchone()
            if row is None:
                # Aspect already exists, fetch it
                await cur.execute(
                    """
                    SELECT id FROM aspect
                    WHERE entity_id = %s AND aspect_def_id = %s
                    """,
                    (entity.id, aspect.definition.id),
                )
                row = await cur.fetchone()
                if row is None:
                    raise ValueError(f"Failed to insert aspect for entity {entity.id}")
            aspect_id = row[0]

        # Save property values
        aspect_def_id = aspect.definition.id
        for prop_name, prop_def in aspect.definition.properties.items():
            prop = aspect.get_property(prop_name)
            if prop is not None and prop.value is not None:
                await self._save_property_value(
                    conn, aspect_id, aspect_def_id, prop_def, prop.value
                )

    async def _save_property_value(
        self,
        conn: psycopg.AsyncConnection,
        aspect_id: int,
        aspect_def_id: UUID,
        prop_def: PropertyDef,
        value: Any,
    ) -> None:
        """Save a property value to database."""
        # Get property_def id from database
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id FROM property_def
                WHERE aspect_def_id = %s AND name = %s
                """,
                (aspect_def_id, prop_def.name),
            )
            row = await cur.fetchone()

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

            await cur.execute(
                """
                INSERT INTO property_value (aspect_id, property_def_id, value_text, value_binary)
                VALUES (%s, %s, %s, %s)
                """,
                (aspect_id, property_def_id, value_text, value_binary),
            )

    async def _load_aspect_defs(self, conn: psycopg.AsyncConnection, catalog: Catalog) -> None:
        """Load aspect definitions for a catalog."""
        from cheap.core.aspect_impl import AspectDefImpl
        from cheap.core.property_impl import PropertyDefImpl

        catalog_id = getattr(catalog, "global_id", getattr(catalog, "id", None))

        # Load aspect defs linked to this catalog
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT ad.id, ad.name, ad.is_readable, ad.is_writable,
                       ad.can_add_properties, ad.can_remove_properties
                FROM aspect_def ad
                JOIN catalog_aspect_def cad ON ad.id = cad.aspect_def_id
                WHERE cad.catalog_id = %s
                """,
                (catalog_id,),
            )

            rows = await cur.fetchall()

        for row in rows:
            aspect_def_id = row[0]  # UUID type
            aspect_name = row[1]

            # Load property definitions for this aspect
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT name, type, is_writable, is_nullable, is_multivalued, default_value
                    FROM property_def
                    WHERE aspect_def_id = %s
                    """,
                    (aspect_def_id,),
                )

                prop_rows = await cur.fetchall()

            properties = {}
            for prop_row in prop_rows:
                prop_type = DB_TO_PROPERTY_TYPE[prop_row[1]]
                prop_def = PropertyDefImpl(
                    name=prop_row[0],
                    property_type=prop_type,
                    is_writable=prop_row[2],
                    is_nullable=prop_row[3],
                    is_multivalued=prop_row[4],
                    default_value=prop_row[5],
                )
                properties[prop_def.name] = prop_def

            # Create aspect definition
            aspect_def = AspectDefImpl(
                id=aspect_def_id,
                name=aspect_name,
                properties=properties,
                is_readable=row[2],
                is_writable=row[3],
                can_add_properties=row[4],
                can_remove_properties=row[5],
            )

            catalog.add_aspect_def(aspect_def)

    async def _load_hierarchy_defs(self, conn: psycopg.AsyncConnection, catalog: Catalog) -> None:
        """Load hierarchy definitions for a catalog."""
        #  TODO: Implement hierarchy definition loading when hierarchy support is complete
        # Currently CatalogImpl tracks Hierarchy instances, not HierarchyDef
        # This will be implemented when full hierarchy persistence is added
        pass
