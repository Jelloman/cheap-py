"""Tests for SQLite adapter."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from cheap.db.sqlite.adapter import SqliteAdapter


class TestSqliteAdapter:
    """Test suite for SqliteAdapter."""

    @pytest.mark.asyncio
    async def test_create_memory_database(self) -> None:
        """Test creating an in-memory database."""
        adapter = await SqliteAdapter.create(":memory:")

        assert adapter.is_memory
        assert adapter.is_connected
        assert adapter.db_path == ":memory:"

        await adapter.close()
        assert not adapter.is_connected

    @pytest.mark.asyncio
    async def test_create_file_database(self) -> None:
        """Test creating a file-based database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            adapter = await SqliteAdapter.create(db_path)

            assert not adapter.is_memory
            assert adapter.is_connected
            assert db_path.exists()

            await adapter.close()

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test using adapter as async context manager."""
        async with await SqliteAdapter.create(":memory:") as adapter:
            assert adapter.is_connected
            conn = await adapter.get_connection()
            assert conn is not None

        # Should be closed after exiting context
        assert not adapter.is_connected

    @pytest.mark.asyncio
    async def test_get_connection_not_connected(self) -> None:
        """Test getting connection when not connected raises error."""
        adapter = SqliteAdapter(":memory:")

        with pytest.raises(RuntimeError, match="Not connected to database"):
            await adapter.get_connection()

    @pytest.mark.asyncio
    async def test_foreign_keys_enabled(self) -> None:
        """Test that foreign keys are enabled by default."""
        async with await SqliteAdapter.create(":memory:") as adapter:
            conn = await adapter.get_connection()

            cursor = await conn.execute("PRAGMA foreign_keys")
            result = await cursor.fetchone()
            await cursor.close()

            assert result[0] == 1  # Foreign keys enabled

    @pytest.mark.asyncio
    async def test_init_schema_on_create(self) -> None:
        """Test initializing schema during adapter creation."""
        adapter = await SqliteAdapter.create(":memory:", init_schema=True)

        conn = await adapter.get_connection()

        # Verify schema was created
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='catalog'"
        )
        result = await cursor.fetchone()
        await cursor.close()

        assert result is not None
        assert result[0] == "catalog"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_repr(self) -> None:
        """Test string representation."""
        adapter = await SqliteAdapter.create(":memory:")
        repr_str = repr(adapter)

        assert "SqliteAdapter" in repr_str
        assert ":memory:" in repr_str
        assert "connected" in repr_str

        await adapter.close()

        repr_str = repr(adapter)
        assert "disconnected" in repr_str
