"""MariaDB/MySQL Data Access Object for catalog persistence."""

from __future__ import annotations

from uuid import UUID

from cheap.core.aspect import AspectDef
from cheap.core.aspect_impl import AspectDefImpl
from cheap.core.catalog import Catalog
from cheap.core.catalog_impl import CatalogImpl
from cheap.core.catalog_species import CatalogSpecies
from cheap.core.property import PropertyDef
from cheap.core.property_impl import PropertyDefImpl
from cheap.core.property_type import PropertyType
from cheap.db.mariadb.adapter import MariaDbAdapter

# Property type mapping to database abbreviations
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

# Reverse mapping from database abbreviations to PropertyType
DB_TO_PROPERTY_TYPE = {v: k for k, v in PROPERTY_TYPE_TO_DB.items()}


class MariaDbDao:
    """Data Access Object for persisting catalogs to MariaDB/MySQL."""

    def __init__(self, adapter: MariaDbAdapter) -> None:
        """Initialize the DAO with a database adapter.

        Args:
            adapter: MariaDB database adapter
        """
        self._adapter = adapter

    async def save_catalog(self, catalog: Catalog) -> None:
        """Save a catalog to the database.

        Args:
            catalog: Catalog to save
        """
        conn = await self._adapter.get_connection()
        try:
            # Save catalog metadata
            await self._save_catalog_metadata(conn, catalog)

            # Save aspect definitions
            aspect_defs = getattr(catalog, "_aspect_defs", {})
            for aspect_def in aspect_defs.values():
                await self._save_aspect_def(conn, catalog, aspect_def)

            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await self._adapter.return_connection(conn)

    async def load_catalog(self, catalog_id: UUID) -> Catalog:
        """Load a catalog from the database.

        Args:
            catalog_id: UUID of the catalog to load

        Returns:
            Loaded catalog instance

        Raises:
            ValueError: If catalog not found
        """
        conn = await self._adapter.get_connection()
        try:
            # Load catalog metadata
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT species, uri, upstream_catalog_id, version_number
                    FROM catalog
                    WHERE catalog_id = %s
                    """,
                    (str(catalog_id),),
                )
                row = await cur.fetchone()

            if not row:
                raise ValueError(f"Catalog not found: {catalog_id}")

            species_str, uri, upstream_id, version = row
            species = CatalogSpecies(species_str)

            # Create catalog
            catalog = CatalogImpl(
                global_id=catalog_id,
                species=species,
                version=str(version),
            )

            # Load aspect definitions
            aspect_defs = await self._load_aspect_defs(conn, catalog_id)
            for aspect_def in aspect_defs.values():
                catalog.add_aspect_def(aspect_def)

            return catalog
        finally:
            await self._adapter.return_connection(conn)

    async def delete_catalog(self, catalog_id: UUID) -> None:
        """Delete a catalog and all its data from the database.

        Args:
            catalog_id: UUID of the catalog to delete
        """
        conn = await self._adapter.get_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM catalog WHERE catalog_id = %s",
                    (str(catalog_id),),
                )
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await self._adapter.return_connection(conn)

    async def _save_catalog_metadata(
        self,
        conn,
        catalog: Catalog,  # type: ignore[no-untyped-def]
    ) -> None:
        """Save catalog metadata to the database."""
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO catalog (catalog_id, species, uri, upstream_catalog_id, version_number)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    species = VALUES(species),
                    uri = VALUES(uri),
                    upstream_catalog_id = VALUES(upstream_catalog_id),
                    version_number = VALUES(version_number)
                """,
                (
                    str(catalog.global_id),
                    catalog.species.value,
                    None,  # URI not yet implemented
                    None,  # Upstream catalog not yet implemented
                    int(catalog.version) if catalog.version.isdigit() else 0,
                ),
            )

    async def _save_aspect_def(  # type: ignore[no-untyped-def]
        self, conn, catalog: Catalog, aspect_def: AspectDef
    ) -> None:
        """Save an aspect definition to the database."""
        aspect_def_id = getattr(aspect_def, "_id", None)
        if aspect_def_id is None:
            # Generate ID if not present
            from uuid import uuid4

            aspect_def_id = uuid4()
            object.__setattr__(aspect_def, "_id", aspect_def_id)

        # Save aspect_def record
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO aspect_def (aspect_def_id, name, hash_version,
                                        is_readable, is_writable,
                                        can_add_properties, can_remove_properties)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    hash_version = VALUES(hash_version),
                    is_readable = VALUES(is_readable),
                    is_writable = VALUES(is_writable),
                    can_add_properties = VALUES(can_add_properties),
                    can_remove_properties = VALUES(can_remove_properties)
                """,
                (
                    str(aspect_def_id),
                    aspect_def.name,
                    None,  # hash_version not yet implemented
                    True,  # is_readable
                    True,  # is_writable
                    False,  # can_add_properties
                    False,  # can_remove_properties
                ),
            )

        # Link to catalog
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO catalog_aspect_def (catalog_id, aspect_def_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE catalog_id = catalog_id
                """,
                (str(catalog.global_id), str(aspect_def_id)),
            )

        # Save property definitions
        properties = getattr(aspect_def, "properties", {})
        for idx, (prop_name, prop_def) in enumerate(properties.items()):
            await self._save_property_def(conn, aspect_def_id, idx, prop_name, prop_def)

    async def _save_property_def(  # type: ignore[no-untyped-def]
        self, conn, aspect_def_id: UUID, index: int, name: str, prop_def: PropertyDef
    ) -> None:
        """Save a property definition to the database."""
        db_type = PROPERTY_TYPE_TO_DB[prop_def.property_type]

        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO property_def (aspect_def_id, name, property_index, property_type,
                                         default_value, has_default_value,
                                         is_readable, is_writable, is_nullable, is_multivalued)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    property_index = VALUES(property_index),
                    property_type = VALUES(property_type),
                    default_value = VALUES(default_value),
                    has_default_value = VALUES(has_default_value),
                    is_readable = VALUES(is_readable),
                    is_writable = VALUES(is_writable),
                    is_nullable = VALUES(is_nullable),
                    is_multivalued = VALUES(is_multivalued)
                """,
                (
                    str(aspect_def_id),
                    name,
                    index,
                    db_type,
                    None,  # default_value not yet implemented
                    False,  # has_default_value
                    True,  # is_readable
                    True,  # is_writable
                    prop_def.is_nullable,
                    False,  # is_multivalued not yet implemented
                ),
            )

    async def _load_aspect_defs(  # type: ignore[no-untyped-def]
        self, conn, catalog_id: UUID
    ) -> dict[str, AspectDef]:
        """Load all aspect definitions for a catalog."""
        aspect_defs: dict[str, AspectDef] = {}

        # Load aspect definitions linked to this catalog
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT ad.aspect_def_id, ad.name, ad.hash_version,
                       ad.is_readable, ad.is_writable,
                       ad.can_add_properties, ad.can_remove_properties
                FROM aspect_def ad
                INNER JOIN catalog_aspect_def cad ON ad.aspect_def_id = cad.aspect_def_id
                WHERE cad.catalog_id = %s
                """,
                (str(catalog_id),),
            )
            rows = await cur.fetchall()

        for row in rows:
            (
                aspect_def_id,
                name,
                hash_version,
                is_readable,
                is_writable,
                can_add_properties,
                can_remove_properties,
            ) = row

            # Load property definitions for this aspect
            properties = await self._load_property_defs(conn, UUID(aspect_def_id))

            # Create AspectDef
            aspect_def = AspectDefImpl(name=name, properties=properties)
            object.__setattr__(aspect_def, "_id", UUID(aspect_def_id))

            aspect_defs[name] = aspect_def

        return aspect_defs

    async def _load_property_defs(  # type: ignore[no-untyped-def]
        self, conn, aspect_def_id: UUID
    ) -> dict[str, PropertyDef]:
        """Load all property definitions for an aspect."""
        properties: dict[str, PropertyDef] = {}

        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT name, property_index, property_type, default_value,
                       has_default_value, is_readable, is_writable,
                       is_nullable, is_multivalued
                FROM property_def
                WHERE aspect_def_id = %s
                ORDER BY property_index
                """,
                (str(aspect_def_id),),
            )
            rows = await cur.fetchall()

        for row in rows:
            (
                name,
                property_index,
                property_type_str,
                default_value,
                has_default_value,
                is_readable,
                is_writable,
                is_nullable,
                is_multivalued,
            ) = row

            property_type = DB_TO_PROPERTY_TYPE[property_type_str]

            prop_def = PropertyDefImpl(
                name=name,
                property_type=property_type,
                is_nullable=bool(is_nullable),
            )

            properties[name] = prop_def

        return properties
