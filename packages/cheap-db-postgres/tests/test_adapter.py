"""Tests for PostgreSQL adapter."""

from __future__ import annotations

import os

import pytest
from cheap.db.postgres.adapter import PostgresAdapter

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


class TestPostgresAdapter:
    """Test suite for PostgresAdapter."""

    @pytest.mark.asyncio
    async def test_create_without_pool(self) -> None:
        """Test creating adapter without connection pooling."""
        adapter = await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        assert not adapter.has_pool
        assert adapter.is_connected

        # Can get standalone connection
        conn = await adapter.get_connection()
        assert conn is not None
        await adapter.return_connection(conn)

        await adapter.close()
        assert not adapter.is_connected

    @pytest.mark.asyncio
    async def test_create_with_pool(self) -> None:
        """Test creating adapter with connection pooling."""
        adapter = await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            pool_size=10,
            min_size=2,
        )

        assert adapter.has_pool
        assert adapter.is_connected

        # Can get pooled connection
        conn = await adapter.get_connection()
        assert conn is not None
        await adapter.return_connection(conn)

        await adapter.close()
        assert not adapter.is_connected

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test using adapter as async context manager."""
        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        ) as adapter:
            assert adapter.is_connected
            conn = await adapter.get_connection()
            assert conn is not None
            await adapter.return_connection(conn)

        # Should be closed after exiting context
        assert not adapter.is_connected

    @pytest.mark.asyncio
    async def test_get_connection_not_connected(self) -> None:
        """Test getting connection when not connected raises error."""
        adapter = PostgresAdapter(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        with pytest.raises(RuntimeError, match="Not connected to database"):
            await adapter.get_connection()

    @pytest.mark.asyncio
    async def test_timezone_set_to_utc(self) -> None:
        """Test that timezone is automatically set to UTC."""
        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        ) as adapter:
            conn = await adapter.get_connection()

            async with conn.cursor() as cur:
                await cur.execute("SHOW TIME ZONE")
                result = await cur.fetchone()

            assert result is not None
            assert result[0].upper() == "UTC"

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_init_schema_on_create(self) -> None:
        """Test initializing schema during adapter creation."""
        from cheap.db.postgres.schema import PostgresSchema

        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            init_schema=True,
        ) as adapter:
            conn = await adapter.get_connection()

            # Verify schema was created
            assert await PostgresSchema.schema_exists(conn)

            # Clean up
            await PostgresSchema.drop_schema(conn)

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_multiple_connections_from_pool(self) -> None:
        """Test acquiring multiple connections from pool."""
        async with await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            pool_size=5,
        ) as adapter:
            # Acquire multiple connections
            conn1 = await adapter.get_connection()
            conn2 = await adapter.get_connection()
            conn3 = await adapter.get_connection()

            assert conn1 is not None
            assert conn2 is not None
            assert conn3 is not None

            # Return connections to pool
            await adapter.return_connection(conn1)
            await adapter.return_connection(conn2)
            await adapter.return_connection(conn3)

    @pytest.mark.asyncio
    async def test_repr(self) -> None:
        """Test string representation."""
        adapter = await PostgresAdapter.create(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        repr_str = repr(adapter)

        assert "PostgresAdapter" in repr_str
        assert POSTGRES_DB in repr_str
        assert "connected" in repr_str

        await adapter.close()

        repr_str = repr(adapter)
        assert "disconnected" in repr_str
