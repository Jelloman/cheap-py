"""Tests for SQLite schema management."""

from __future__ import annotations

import pytest
from cheap.db.sqlite.adapter import SqliteAdapter
from cheap.db.sqlite.schema import SqliteSchema


class TestSqliteSchema:
    """Test suite for SQLite schema operations."""

    @pytest.mark.asyncio
    async def test_create_schema(self) -> None:
        """Test creating the CHEAP schema."""
        async with await SqliteAdapter.create(":memory:") as adapter:
            conn = await adapter.get_connection()

            # Schema should not exist initially
            assert not await SqliteSchema.schema_exists(conn)

            # Create schema
            await SqliteSchema.create_schema(conn, include_audit=False)

            # Schema should now exist
            assert await SqliteSchema.schema_exists(conn)

            # Verify key tables exist
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in await cursor.fetchall()]
            await cursor.close()

            expected_tables = [
                "aspect",
                "aspect_def",
                "catalog",
                "catalog_aspect_def",
                "entity",
                "hierarchy",
                "hierarchy_aspect_map",
                "hierarchy_def",
                "hierarchy_entity_directory",
                "hierarchy_entity_list",
                "hierarchy_entity_set",
                "hierarchy_entity_tree_node",
                "property_def",
                "property_value",
            ]

            for table in expected_tables:
                assert table in tables, f"Table {table} not found"

    @pytest.mark.asyncio
    async def test_create_schema_with_audit(self) -> None:
        """Test creating schema with audit functionality."""
        async with await SqliteAdapter.create(":memory:") as adapter:
            conn = await adapter.get_connection()

            # Create schema with audit
            await SqliteSchema.create_schema(conn, include_audit=True)

            # Check that audit columns exist in aspect_def
            cursor = await conn.execute("PRAGMA table_info(aspect_def)")
            columns = [row[1] for row in await cursor.fetchall()]
            await cursor.close()

            assert "created_at" in columns
            assert "updated_at" in columns

            # Check that triggers exist
            cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
            triggers = [row[0] for row in await cursor.fetchall()]
            await cursor.close()

            assert "update_aspect_def_updated_at" in triggers
            assert "update_catalog_updated_at" in triggers

    @pytest.mark.asyncio
    async def test_drop_schema(self) -> None:
        """Test dropping the schema."""
        async with await SqliteAdapter.create(":memory:") as adapter:
            conn = await adapter.get_connection()

            # Create then drop schema
            await SqliteSchema.create_schema(conn)
            assert await SqliteSchema.schema_exists(conn)

            await SqliteSchema.drop_schema(conn)
            assert not await SqliteSchema.schema_exists(conn)

    @pytest.mark.asyncio
    async def test_truncate_data(self) -> None:
        """Test truncating data while preserving schema."""
        async with await SqliteAdapter.create(":memory:") as adapter:
            conn = await adapter.get_connection()

            # Create schema
            await SqliteSchema.create_schema(conn)

            # Insert test data
            await conn.execute(
                """
                INSERT INTO aspect_def (id, name)
                VALUES ('550e8400-e29b-41d4-a716-446655440000', 'test_aspect')
                """
            )
            await conn.commit()

            # Verify data exists
            cursor = await conn.execute("SELECT COUNT(*) FROM aspect_def")
            count = (await cursor.fetchone())[0]
            await cursor.close()
            assert count == 1

            # Truncate data
            await SqliteSchema.truncate_data(conn)

            # Verify data is gone but schema remains
            assert await SqliteSchema.schema_exists(conn)

            cursor = await conn.execute("SELECT COUNT(*) FROM aspect_def")
            count = (await cursor.fetchone())[0]
            await cursor.close()
            assert count == 0

    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self) -> None:
        """Test that foreign key constraints are enforced."""
        async with await SqliteAdapter.create(":memory:") as adapter:
            conn = await adapter.get_connection()
            await SqliteSchema.create_schema(conn)

            # Attempt to insert property_def with non-existent aspect_def
            with pytest.raises(Exception):  # aiosqlite.IntegrityError
                await conn.execute(
                    """
                    INSERT INTO property_def (aspect_def_id, name, type)
                    VALUES ('nonexistent-id', 'test_prop', 'STR')
                    """
                )
                await conn.commit()
