"""SQLite database connection adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Self

import aiosqlite


class SqliteAdapter:
    """
    SQLite database connection adapter.

    Manages async SQLite database connections with proper lifecycle management.
    Supports both file-based and in-memory databases.

    Example:
        ```python
        # File-based database
        adapter = await SqliteAdapter.create("data/catalog.db")
        async with adapter.connection() as conn:
            # Use connection
            pass
        await adapter.close()

        # In-memory database
        adapter = await SqliteAdapter.create(":memory:")
        ```
    """

    def __init__(self, db_path: str | Path) -> None:
        """
        Initialize adapter (use create() instead).

        Args:
            db_path: Path to database file or ":memory:" for in-memory database.
        """
        self._db_path = str(db_path)
        self._conn: aiosqlite.Connection | None = None

    @classmethod
    async def create(
        cls,
        db_path: str | Path,
        *,
        init_schema: bool = False,
        include_audit: bool = False,
    ) -> Self:
        """
        Create and initialize a SQLite adapter.

        Args:
            db_path: Path to database file or ":memory:" for in-memory database.
            init_schema: If True, initialize the CHEAP schema.
            include_audit: If True and init_schema is True, include audit tables.

        Returns:
            Initialized SqliteAdapter.

        Example:
            ```python
            # Create with schema initialization
            adapter = await SqliteAdapter.create(
                "data/catalog.db",
                init_schema=True,
                include_audit=True
            )
            ```
        """
        adapter = cls(db_path)
        await adapter.connect()

        if init_schema:
            from cheap.db.sqlite.schema import SqliteSchema

            conn = await adapter.get_connection()
            await SqliteSchema.create_schema(conn, include_audit=include_audit)

        return adapter

    async def connect(self) -> None:
        """
        Establish database connection.

        Raises:
            aiosqlite.Error: If connection fails.
        """
        if self._conn is not None:
            return

        self._conn = await aiosqlite.connect(self._db_path)

        # Enable foreign key support
        await self._conn.execute("PRAGMA foreign_keys = ON")

        # Enable WAL mode for better concurrency (not for in-memory)
        if self._db_path != ":memory:":
            await self._conn.execute("PRAGMA journal_mode = WAL")

        await self._conn.commit()

    async def close(self) -> None:
        """Close database connection."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def get_connection(self) -> aiosqlite.Connection:
        """
        Get the database connection.

        Returns:
            Active database connection.

        Raises:
            RuntimeError: If not connected.
        """
        if self._conn is None:
            raise RuntimeError("Not connected to database. Call connect() first.")
        return self._conn

    @property
    def db_path(self) -> str:
        """Get the database path."""
        return self._db_path

    @property
    def is_memory(self) -> bool:
        """Check if this is an in-memory database."""
        return self._db_path == ":memory:"

    @property
    def is_connected(self) -> bool:
        """Check if currently connected."""
        return self._conn is not None

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        """String representation."""
        status = "connected" if self.is_connected else "disconnected"
        return f"SqliteAdapter(db_path={self._db_path!r}, status={status})"
