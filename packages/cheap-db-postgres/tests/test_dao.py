"""Tests for PostgreSQL DAO catalog persistence."""

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
from cheap.db.postgres.adapter import PostgresAdapter
from cheap.db.postgres.dao import PostgresDao
from cheap.db.postgres.schema import PostgresSchema

# PostgreSQL connection parameters from environment
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "cheap_test")
POSTGRES_USER = os.getenv("POSTGRES_USER", "cheap_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Skip all tests if PostgreSQL is not available
pytestmark = pytest.mark.skipif(
    not os.getenv("POSTGRES_AVAILABLE", ""),
    reason="PostgreSQL not available (set POSTGRES_AVAILABLE=1 to enable)",
)


class TestPostgresDao:
    """Test suite for PostgresDao catalog persistence."""

    @pytest.fixture
    async def adapter(self) -> AsyncGenerator[PostgresAdapter, None]:
        """Create an adapter with schema."""
        adapter = await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            init_schema=True,
        )

        # Clean any existing data
        conn = await adapter.get_connection()
        await PostgresSchema.truncate_data(conn)
        await adapter.return_connection(conn)

        yield adapter
        await adapter.close()

    @pytest.fixture
    def dao(self, adapter: PostgresAdapter) -> PostgresDao:
        """Create a DAO instance."""
        return PostgresDao(adapter)

    @pytest.mark.asyncio
    async def test_save_and_load_empty_catalog(
        self, adapter: PostgresAdapter, dao: PostgresDao
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
        self, adapter: PostgresAdapter, dao: PostgresDao
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
    async def test_delete_catalog(self, adapter: PostgresAdapter, dao: PostgresDao) -> None:
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
    async def test_load_nonexistent_catalog(
        self, adapter: PostgresAdapter, dao: PostgresDao
    ) -> None:
        """Test loading a non-existent catalog raises error."""
        nonexistent_id = uuid4()

        with pytest.raises(ValueError, match="Catalog not found"):
            await dao.load_catalog(nonexistent_id)

    @pytest.mark.asyncio
    async def test_property_type_mapping(self, adapter: PostgresAdapter, dao: PostgresDao) -> None:
        """Test that all property types are correctly mapped."""
        from cheap.db.postgres.dao import DB_TO_PROPERTY_TYPE, PROPERTY_TYPE_TO_DB

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
    async def test_upsert_catalog(self, adapter: PostgresAdapter, dao: PostgresDao) -> None:
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
    async def test_native_uuid_type(self, adapter: PostgresAdapter, dao: PostgresDao) -> None:
        """Test that PostgreSQL native UUID type is used."""
        catalog_id = uuid4()
        catalog = CatalogImpl(
            global_id=catalog_id,
            species=CatalogSpecies.SOURCE,
            version="1.0.0",
        )

        await dao.save_catalog(catalog)

        # Verify UUID is stored as native PostgreSQL UUID type
        conn = await adapter.get_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT pg_typeof(id) FROM catalog WHERE id = %s
                    """,
                    (catalog_id,),
                )
                result = await cur.fetchone()

            assert result is not None
            # PostgreSQL returns 'uuid' as the type name
            assert result[0] == "uuid"
        finally:
            await adapter.return_connection(conn)
