"""MariaDB/MySQL connection adapter for Cheap."""

from __future__ import annotations

from typing import Self

import aiomysql

from cheap.db.mariadb.schema import MariaDbSchema


class MariaDbAdapter:
    """Adapter for managing async MariaDB/MySQL database connections.

    Supports both connection pooling (production) and standalone connections (development/testing).
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        db: str = "cheap",
        user: str = "cheap_user",
        password: str = "",
        charset: str = "utf8mb4",
    ) -> None:
        """Initialize the adapter (does not connect).

        Args:
            host: MariaDB/MySQL server hostname
            port: Server port
            db: Database name
            user: Database user
            password: Database password
            charset: Character set (default: utf8mb4)
        """
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.charset = charset
        self._pool: aiomysql.Pool | None = None
        self._standalone_conn: aiomysql.Connection | None = None

    @classmethod
    async def create(
        cls,
        host: str = "localhost",
        port: int = 3306,
        db: str = "cheap",
        user: str = "cheap_user",
        password: str = "",
        charset: str = "utf8mb4",
        *,
        pool_size: int | None = None,
        min_size: int | None = None,
        init_schema: bool = False,
        include_audit: bool = False,
        include_foreign_keys: bool = False,
    ) -> Self:
        """Create and connect a new adapter.

        Args:
            host: MariaDB/MySQL server hostname
            port: Server port
            db: Database name
            user: Database user
            password: Database password
            charset: Character set (default: utf8mb4)
            pool_size: Maximum pool size (None = standalone connection)
            min_size: Minimum pool size (default: 5)
            init_schema: If True, create schema on first connect
            include_audit: If True, include audit columns when creating schema
            include_foreign_keys: If True, include FK constraints when creating schema

        Returns:
            Connected adapter instance
        """
        adapter = cls(host, port, db, user, password, charset)

        # Create pool or standalone connection
        if pool_size is not None:
            # Connection pooling for production
            adapter._pool = await aiomysql.create_pool(
                host=host,
                port=port,
                db=db,
                user=user,
                password=password,
                charset=charset,
                minsize=min_size or 5,
                maxsize=pool_size,
                autocommit=False,
            )
        else:
            # Standalone connection for development/testing
            adapter._standalone_conn = await aiomysql.connect(
                host=host,
                port=port,
                db=db,
                user=user,
                password=password,
                charset=charset,
                autocommit=False,
            )

        # Initialize schema if requested
        if init_schema:
            conn = await adapter.get_connection()
            try:
                await MariaDbSchema.create_schema(
                    conn,
                    include_audit=include_audit,
                    include_foreign_keys=include_foreign_keys,
                )
            finally:
                await adapter.return_connection(conn)

        return adapter

    @property
    def has_pool(self) -> bool:
        """Check if this adapter uses connection pooling."""
        return self._pool is not None

    @property
    def is_connected(self) -> bool:
        """Check if the adapter is connected to the database."""
        if self._pool is not None:
            return not self._pool.closed
        if self._standalone_conn is not None:
            return not self._standalone_conn.closed
        return False

    async def get_connection(self) -> aiomysql.Connection:
        """Get a database connection.

        For pooled adapters, acquires a connection from the pool.
        For standalone adapters, returns the standalone connection.

        Returns:
            Active database connection

        Raises:
            RuntimeError: If not connected to database
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to database")

        if self._pool is not None:
            # Acquire from pool
            return await self._pool.acquire()
        elif self._standalone_conn is not None:
            # Return standalone connection
            return self._standalone_conn
        else:
            raise RuntimeError("No connection available")

    async def return_connection(self, conn: aiomysql.Connection) -> None:
        """Return a connection to the pool (or no-op for standalone).

        Args:
            conn: Connection to return
        """
        if self._pool is not None:
            # Return to pool
            self._pool.release(conn)
        # For standalone connections, do nothing (conn is reused)

    async def connection(self) -> aiomysql.Connection:
        """Get a connection (alias for get_connection for compatibility).

        Returns:
            Active database connection
        """
        return await self.get_connection()

    async def close(self) -> None:
        """Close all connections and clean up resources."""
        if self._pool is not None:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None

        if self._standalone_conn is not None:
            self._standalone_conn.close()
            self._standalone_conn = None

    async def __aenter__(self) -> Self:
        """Enter async context (already connected)."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Exit async context and close connections."""
        await self.close()

    def __repr__(self) -> str:
        """String representation of the adapter."""
        status = "connected" if self.is_connected else "disconnected"
        mode = "pooled" if self.has_pool else "standalone"
        return f"MariaDbAdapter({self.db}@{self.host}:{self.port}, {mode}, {status})"
