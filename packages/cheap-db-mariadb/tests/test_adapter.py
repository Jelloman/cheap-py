"""Tests for MariaDB adapter."""

from __future__ import annotations

import os

import pytest
from cheap.db.mariadb.adapter import MariaDbAdapter

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


class TestMariaDbAdapter:
    """Test suite for MariaDbAdapter."""

    @pytest.mark.asyncio
    async def test_create_without_pool(self) -> None:
        """Test creating adapter without connection pooling."""
        adapter = await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
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
        adapter = await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
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
        async with await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
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
        adapter = MariaDbAdapter(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
        )

        with pytest.raises(RuntimeError, match="Not connected to database"):
            await adapter.get_connection()

    @pytest.mark.asyncio
    async def test_init_schema_on_create(self) -> None:
        """Test initializing schema during adapter creation."""
        from cheap.db.mariadb.schema import MariaDbSchema

        async with await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
            init_schema=True,
        ) as adapter:
            conn = await adapter.get_connection()

            # Verify schema was created
            assert await MariaDbSchema.schema_exists(conn)

            # Clean up
            await MariaDbSchema.drop_schema(conn)

            await adapter.return_connection(conn)

    @pytest.mark.asyncio
    async def test_multiple_connections_from_pool(self) -> None:
        """Test acquiring multiple connections from pool."""
        async with await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
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
        adapter = await MariaDbAdapter.create(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            db=MARIADB_DB,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
        )

        repr_str = repr(adapter)

        assert "MariaDbAdapter" in repr_str
        assert MARIADB_DB in repr_str
        assert "connected" in repr_str

        await adapter.close()

        repr_str = repr(adapter)
        assert "disconnected" in repr_str
