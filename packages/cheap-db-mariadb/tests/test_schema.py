"""Tests for MariaDB schema management."""

from __future__ import annotations

import os

import aiomysql
import pytest
from cheap.db.mariadb.adapter import MariaDbAdapter
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


class TestMariaDbSchema:
    """Test suite for MariaDB schema operations."""

    @pytest.mark.asyncio
    async def test_create_schema(self) -> None:
        """Test creating the CHEAP schema."""
        async with await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            # Clean up any existing schema
            await MariaDbSchema.drop_schema(conn)

            # Schema should not exist initially
            assert not await MariaDbSchema.schema_exists(conn)

            # Create schema
            await MariaDbSchema.create_schema(conn, include_audit=False, include_foreign_keys=False)

            # Schema should now exist
            assert await MariaDbSchema.schema_exists(conn)

            # Verify key tables exist
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """
                )
                rows = await cur.fetchall()
                tables = [row[0] for row in rows]

            expected_tables = [
                "aspect",
                "aspect_def",
                "catalog",
                "catalog_aspect_def",
                "hierarchy",
                "hierarchy_aspect_map",
                "hierarchy_entity_directory",
                "hierarchy_entity_list",
                "hierarchy_entity_set",
                "hierarchy_entity_tree_node",
                "property_def",
                "property_value",
            ]

            for table in expected_tables:
                assert table in tables, f"Table {table} not found"

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_create_schema_with_audit(self) -> None:
        """Test creating schema with audit functionality."""
        async with await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            # Clean up and create schema with audit
            await MariaDbSchema.drop_schema(conn)
            await MariaDbSchema.create_schema(conn, include_audit=True, include_foreign_keys=False)

            # Check that audit columns exist in aspect_def
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = 'aspect_def'
                    ORDER BY column_name
                    """
                )
                rows = await cur.fetchall()
                columns = [row[0] for row in rows]

            assert "created_at" in columns
            assert "updated_at" in columns

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_drop_schema(self) -> None:
        """Test dropping the schema."""
        async with await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            # Create then drop schema
            await MariaDbSchema.drop_schema(conn)
            await MariaDbSchema.create_schema(conn)
            assert await MariaDbSchema.schema_exists(conn)

            await MariaDbSchema.drop_schema(conn)
            assert not await MariaDbSchema.schema_exists(conn)

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_truncate_data(self) -> None:
        """Test truncating data while preserving schema."""
        async with await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            # Create schema
            await MariaDbSchema.drop_schema(conn)
            await MariaDbSchema.create_schema(conn)

            # Insert test data
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO aspect_def (aspect_def_id, name)
                    VALUES ('550e8400-e29b-41d4-a716-446655440000', 'test_aspect')
                    """
                )
            await conn.commit()

            # Verify data exists
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM aspect_def")
                row = await cur.fetchone()
                count = row[0] if row else 0

            assert count == 1

            # Truncate data
            await MariaDbSchema.truncate_data(conn)

            # Verify data is gone but schema remains
            assert await MariaDbSchema.schema_exists(conn)

            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM aspect_def")
                row = await cur.fetchone()
                count = row[0] if row else 0

            assert count == 0

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self) -> None:
        """Test that foreign key constraints are enforced when enabled."""
        async with await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            await MariaDbSchema.drop_schema(conn)
            await MariaDbSchema.create_schema(conn, include_foreign_keys=True)

            # Attempt to insert property_def with non-existent aspect_def
            with pytest.raises(aiomysql.IntegrityError):
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO property_def (aspect_def_id, name, property_index, property_type)
                        VALUES ('550e8400-e29b-41d4-a716-446655440000', 'test_prop', 0, 'STR')
                        """
                    )
                await conn.commit()

            await adapter.return_connection(conn)
