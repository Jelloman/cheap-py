"""Tests for PostgreSQL schema management."""

from __future__ import annotations

import os

import psycopg
import pytest
from cheap.db.postgres.adapter import PostgresAdapter
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


class TestPostgresSchema:
    """Test suite for PostgreSQL schema operations."""

    @pytest.mark.asyncio
    async def test_create_schema(self) -> None:
        """Test creating the CHEAP schema."""
        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            # Clean up any existing schema
            await PostgresSchema.drop_schema(conn)

            # Schema should not exist initially
            assert not await PostgresSchema.schema_exists(conn)

            # Create schema
            await PostgresSchema.create_schema(conn, include_audit=False)

            # Schema should now exist
            assert await PostgresSchema.schema_exists(conn)

            # Verify key tables exist
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
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

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_create_schema_with_audit(self) -> None:
        """Test creating schema with audit functionality."""
        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            # Clean up and create schema with audit
            await PostgresSchema.drop_schema(conn)
            await PostgresSchema.create_schema(conn, include_audit=True)

            # Check that audit columns exist in aspect_def
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'aspect_def'
                    ORDER BY column_name
                    """
                )
                rows = await cur.fetchall()
                columns = [row[0] for row in rows]

            assert "created_at" in columns
            assert "updated_at" in columns

            # Check that triggers exist
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT trigger_name FROM information_schema.triggers
                    WHERE trigger_schema = 'public'
                    """
                )
                rows = await cur.fetchall()
                triggers = [row[0] for row in rows]

            assert "update_aspect_def_updated_at" in triggers
            assert "update_catalog_updated_at" in triggers

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_drop_schema(self) -> None:
        """Test dropping the schema."""
        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            # Create then drop schema
            await PostgresSchema.drop_schema(conn)
            await PostgresSchema.create_schema(conn)
            assert await PostgresSchema.schema_exists(conn)

            await PostgresSchema.drop_schema(conn)
            assert not await PostgresSchema.schema_exists(conn)

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_truncate_data(self) -> None:
        """Test truncating data while preserving schema."""
        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            # Create schema
            await PostgresSchema.drop_schema(conn)
            await PostgresSchema.create_schema(conn)

            # Insert test data
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO aspect_def (id, name)
                    VALUES ('550e8400-e29b-41d4-a716-446655440000'::uuid, 'test_aspect')
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
            await PostgresSchema.truncate_data(conn)

            # Verify data is gone but schema remains
            assert await PostgresSchema.schema_exists(conn)

            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM aspect_def")
                row = await cur.fetchone()
                count = row[0] if row else 0

            assert count == 0

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self) -> None:
        """Test that foreign key constraints are enforced."""
        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            await PostgresSchema.drop_schema(conn)
            await PostgresSchema.create_schema(conn)

            # Attempt to insert property_def with non-existent aspect_def
            with pytest.raises(psycopg.errors.ForeignKeyViolation):
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO property_def (aspect_def_id, name, type)
                        VALUES ('550e8400-e29b-41d4-a716-446655440000'::uuid, 'test_prop', 'STR')
                        """
                    )
                await conn.commit()

            await adapter.return_connection(conn)
