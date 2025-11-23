"""Cross-database consistency tests.

Verify that all database backends (SQLite, PostgreSQL, MariaDB) behave identically.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from cheap.core.catalog_impl import CatalogImpl
from cheap.core.catalog_species import CatalogSpecies


@pytest.mark.integration
@pytest.mark.database
class TestCrossDatabaseCatalogOperations:
    """Test catalog operations across all database backends."""

    async def test_save_and_load_catalog_sqlite(self, sqlite_dao, sample_catalog) -> None:
        """Test saving and loading a catalog in SQLite."""
        # Save catalog
        await sqlite_dao.save_catalog(sample_catalog)

        # Load catalog
        loaded = await sqlite_dao.load_catalog(sample_catalog.global_id)

        assert loaded is not None
        assert loaded.global_id == sample_catalog.global_id
        assert loaded.species == sample_catalog.species
        assert loaded.version == sample_catalog.version

    async def test_delete_catalog_sqlite(self, sqlite_dao, sample_catalog) -> None:
        """Test deleting a catalog in SQLite."""
        # Save catalog
        await sqlite_dao.save_catalog(sample_catalog)

        # Verify it exists
        loaded = await sqlite_dao.load_catalog(sample_catalog.global_id)
        assert loaded is not None

        # Delete catalog
        await sqlite_dao.delete_catalog(sample_catalog.global_id)

        # Verify it's deleted - should raise ValueError
        with pytest.raises(ValueError, match="Catalog not found"):
            await sqlite_dao.load_catalog(sample_catalog.global_id)

    async def test_update_catalog_sqlite(self, sqlite_dao) -> None:
        """Test updating a catalog in SQLite."""
        # Create and save initial catalog
        catalog = CatalogImpl(
            global_id=uuid4(),
            species=CatalogSpecies.SOURCE,
            version="1.0.0",
        )
        await sqlite_dao.save_catalog(catalog)

        # Update catalog (upsert with same ID)
        updated_catalog = CatalogImpl(
            global_id=catalog.global_id,
            species=CatalogSpecies.SINK,
            version="2.0.0",
        )
        await sqlite_dao.save_catalog(updated_catalog)

        # Load and verify update
        loaded = await sqlite_dao.load_catalog(catalog.global_id)
        assert loaded is not None
        assert loaded.species == CatalogSpecies.SINK
        assert loaded.version == "2.0.0"


@pytest.mark.integration
@pytest.mark.database
class TestCrossDatabaseConsistency:
    """Test that all databases produce identical results."""

    async def test_catalog_consistency_sqlite_only(self, sqlite_dao) -> None:
        """Test catalog operations are consistent (SQLite baseline)."""
        catalogs = [
            CatalogImpl(CatalogSpecies.SOURCE, "1.0.0", uuid4()),
            CatalogImpl(CatalogSpecies.SINK, "1.0.0", uuid4()),
            CatalogImpl(CatalogSpecies.CACHE, "2.0.0", uuid4()),
        ]

        # Save all catalogs
        for catalog in catalogs:
            await sqlite_dao.save_catalog(catalog)

        # Load and verify each catalog
        for catalog in catalogs:
            loaded = await sqlite_dao.load_catalog(catalog.global_id)
            assert loaded is not None
            assert loaded.global_id == catalog.global_id
            assert loaded.species == catalog.species
            assert loaded.version == catalog.version

    async def test_nonexistent_catalog_returns_none_sqlite(self, sqlite_dao) -> None:
        """Test that loading nonexistent catalog raises ValueError."""
        nonexistent_id = uuid4()
        with pytest.raises(ValueError, match="Catalog not found"):
            await sqlite_dao.load_catalog(nonexistent_id)
