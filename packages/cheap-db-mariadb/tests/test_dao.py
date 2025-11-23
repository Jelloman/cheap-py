"""Tests for MariaDB DAO catalog persistence."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from cheap.core.aspect_impl import AspectDefImpl
from cheap.core.catalog_impl import CatalogImpl
from cheap.core.catalog_species import CatalogSpecies
from cheap.core.property_impl import PropertyDefImpl
from cheap.core.property_type import PropertyType
from cheap.db.mariadb.adapter import MariaDbAdapter
from cheap.db.mariadb.dao import MariaDbDao
from cheap.db.mariadb.schema import MariaDbSchema

# MariaDB connection parameters from environment
MARIADB_HOST = os.getenv("MARIADB_HOST", "localhost")
MARIADB_PORT = int(os.getenv("MARIADB_PORT", "3306"))
MARIADB_DB = os.getenv("MARIADB_DB", "cheap_test")
MARIADB_USER = os.getenv("MARIADB_USER", "cheap_user")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "")

# Skip all tests if MariaDB is not available
pytestmark = pytest.mark.skipif(
    not os.getenv("MARIADB_AVAILABLE", ""),
    reason="MariaDB not available (set MARIADB_AVAILABLE=1 to enable)",
)


class TestMariaDbDao:
    """Test suite for MariaDbDao catalog persistence."""

    @pytest.fixture
    async def adapter(self) -> AsyncGenerator[MariaDbAdapter, None]:
        """Create an adapter with schema."""
        adapter = await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
            init_schema=True,
        )

        # Clean any existing data
        conn = await adapter.get_connection()
        await MariaDbSchema.truncate_data(conn)
        await adapter.return_connection(conn)

        yield adapter
        await adapter.close()

    @pytest.fixture
    def dao(self, adapter: MariaDbAdapter) -> MariaDbDao:
        """Create a DAO instance."""
        return MariaDbDao(adapter)

    @pytest.mark.asyncio
    async def test_save_and_load_empty_catalog(
        self, adapter: MariaDbAdapter, dao: MariaDbDao
    ) -> None:
        """Test saving and loading an empty catalog."""
        # Create empty catalog
        catalog_id = uuid4()
        catalog = CatalogImpl(
            global_id=catalog_id,
            species=CatalogSpecies.SOURCE,
            version="1.0.0",
        )

        # Save catalog
        await dao.save_catalog(catalog)

        # Load catalog
        loaded = await dao.load_catalog(catalog_id)

        assert loaded is not None
        assert str(loaded.global_id) == str(catalog_id)
        assert loaded.species == CatalogSpecies.SOURCE
        assert loaded.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_save_catalog_with_aspect_defs(
        self, adapter: MariaDbAdapter, dao: MariaDbDao
    ) -> None:
        """Test saving a catalog with aspect definitions."""
        # Create catalog with aspect definitions
        catalog_id = uuid4()
        catalog = CatalogImpl(
            global_id=catalog_id,
            species=CatalogSpecies.SOURCE,
            version="1.0.0",
        )

        # Add aspect definition with properties
        prop_def1 = PropertyDefImpl(
            name="name",
            property_type=PropertyType.STRING,
        )
        prop_def2 = PropertyDefImpl(
            name="age",
            property_type=PropertyType.INTEGER,
            is_nullable=False,
        )

        aspect_def = AspectDefImpl(
            name="person",
            properties={"name": prop_def1, "age": prop_def2},
        )

        catalog.add_aspect_def(aspect_def)

        # Save catalog
        await dao.save_catalog(catalog)

        # Load catalog
        loaded = await dao.load_catalog(catalog_id)

        assert loaded is not None
        assert len(loaded.aspect_defs) == 1
        assert "person" in loaded.aspect_defs

        loaded_aspect = loaded.aspect_defs["person"]
        assert loaded_aspect.name == "person"
        assert len(loaded_aspect.properties) == 2
        assert "name" in loaded_aspect.properties
        assert "age" in loaded_aspect.properties

        # Verify property definitions
        loaded_name_prop = loaded_aspect.properties["name"]
        assert loaded_name_prop.name == "name"
        assert loaded_name_prop.property_type == PropertyType.STRING

        loaded_age_prop = loaded_aspect.properties["age"]
        assert loaded_age_prop.name == "age"
        assert loaded_age_prop.property_type == PropertyType.INTEGER
        assert not loaded_age_prop.is_nullable

    @pytest.mark.asyncio
    async def test_delete_catalog(self, adapter: MariaDbAdapter, dao: MariaDbDao) -> None:
        """Test deleting a catalog."""
        # Create and save catalog
        catalog_id = uuid4()
        catalog = CatalogImpl(
            global_id=catalog_id,
            species=CatalogSpecies.SOURCE,
            version="1.0.0",
        )

        await dao.save_catalog(catalog)

        # Verify it exists
        loaded = await dao.load_catalog(catalog_id)
        assert loaded is not None

        # Delete catalog
        await dao.delete_catalog(catalog_id)

        # Verify it's gone
        with pytest.raises(ValueError, match="Catalog not found"):
            await dao.load_catalog(catalog_id)

    @pytest.mark.asyncio
    async def test_load_nonexistent_catalog(self, adapter: MariaDbAdapter, dao: MariaDbDao) -> None:
        """Test loading a non-existent catalog raises error."""
        nonexistent_id = uuid4()

        with pytest.raises(ValueError, match="Catalog not found"):
            await dao.load_catalog(nonexistent_id)

    @pytest.mark.asyncio
    async def test_property_type_mapping(self, adapter: MariaDbAdapter, dao: MariaDbDao) -> None:
        """Test that all property types are correctly mapped."""
        from cheap.db.mariadb.dao import DB_TO_PROPERTY_TYPE, PROPERTY_TYPE_TO_DB

        # Verify bidirectional mapping
        for prop_type, db_type in PROPERTY_TYPE_TO_DB.items():
            assert DB_TO_PROPERTY_TYPE[db_type] == prop_type

        # Verify all PropertyType values are mapped
        all_types = [
            PropertyType.INTEGER,
            PropertyType.FLOAT,
            PropertyType.BOOLEAN,
            PropertyType.STRING,
            PropertyType.TEXT,
            PropertyType.BIG_INTEGER,
            PropertyType.BIG_DECIMAL,
            PropertyType.DATE_TIME,
            PropertyType.URI,
            PropertyType.UUID,
            PropertyType.CLOB,
            PropertyType.BLOB,
        ]

        for prop_type in all_types:
            assert prop_type in PROPERTY_TYPE_TO_DB

    @pytest.mark.asyncio
    async def test_upsert_catalog(self, adapter: MariaDbAdapter, dao: MariaDbDao) -> None:
        """Test that saving the same catalog twice uses upsert."""
        catalog_id = uuid4()
        catalog = CatalogImpl(
            global_id=catalog_id,
            species=CatalogSpecies.SOURCE,
            version="1.0.0",
        )

        # Save catalog
        await dao.save_catalog(catalog)

        # Save again with updated version
        catalog_v2 = CatalogImpl(
            global_id=catalog_id,
            species=CatalogSpecies.SOURCE,
            version="2.0.0",
        )
        await dao.save_catalog(catalog_v2)

        # Load and verify it was updated, not duplicated
        loaded = await dao.load_catalog(catalog_id)
        assert loaded.version == "2.0.0"

    @pytest.mark.asyncio
    async def test_uuid_string_storage(self, adapter: MariaDbAdapter, dao: MariaDbDao) -> None:
        """Test that UUIDs are stored as CHAR(36) strings."""
        catalog_id = uuid4()
        catalog = CatalogImpl(
            global_id=catalog_id,
            species=CatalogSpecies.SOURCE,
            version="1.0.0",
        )

        await dao.save_catalog(catalog)

        # Verify UUID is stored as string
        conn = await adapter.get_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT catalog_id FROM catalog WHERE catalog_id = %s",
                    (str(catalog_id),),
                )
                result = await cur.fetchone()

            assert result is not None
            # MariaDB returns the UUID as a string
            assert result[0] == str(catalog_id)
        finally:
            await adapter.return_connection(conn)
