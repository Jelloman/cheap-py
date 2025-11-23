"""PostgreSQL database connection adapter with pooling support."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

import psycopg
from psycopg_pool import AsyncConnectionPool

if TYPE_CHECKING:
    from psycopg.rows import TupleRow


class PostgresAdapter:
    """
    PostgreSQL database connection adapter with async support and pooling.

    Manages async PostgreSQL database connections with connection pooling
    for production deployments. Automatically sets timezone to UTC.

    Example:
        ```python
        # With connection pooling (recommended for production)
        adapter = await PostgresAdapter.create(
            host="localhost",
            port=5432,
            dbname="cheap",
            user="cheap_user",
            password="password",
            pool_size=10,
            min_size=5,
        )

        async with adapter.connection() as conn:
            # Use connection
            pass

        await adapter.close()
        ```
    """

    def __init__(
        self,
        conninfo: str,
        pool: AsyncConnectionPool | None = None,
    ) -> None:
        """
        Initialize adapter (use create() instead).

        Args:
            conninfo: PostgreSQL connection string.
            pool: Optional connection pool.
        """
        self._conninfo = conninfo
        self._pool = pool
        self._standalone_conn: psycopg.AsyncConnection[TupleRow] | None = None

    @classmethod
    async def create(
        cls,
        host: str = "localhost",
        port: int = 5432,
        dbname: str = "cheap",
        user: str = "cheap_user",
        password: str = "",
        *,
        pool_size: int | None = None,
        min_size: int | None = None,
        init_schema: bool = False,
        include_audit: bool = False,
    ) -> Self:
        """
        Create and initialize a PostgreSQL adapter.

        Args:
            host: Database host.
            port: Database port.
            dbname: Database name.
            user: Database user.
            password: Database password.
            pool_size: Maximum pool size (None for no pooling).
            min_size: Minimum pool size.
            init_schema: If True, initialize the CHEAP schema.
            include_audit: If True and init_schema is True, include audit tables.

        Returns:
            Initialized PostgresAdapter.

        Example:
            ```python
            # Production with pooling
            adapter = await PostgresAdapter.create(
                host="localhost",
                dbname="cheap",
                user="cheap_user",
                password="secret",
                pool_size=10,
                min_size=5,
            )

            # Simple (no pooling)
            adapter = await PostgresAdapter.create(
                host="localhost",
                dbname="cheap",
                user="cheap_user",
            )
            ```
        """
        # Build connection string
        conninfo = f"host={host} port={port} dbname={dbname} user={user}"
        if password:
            conninfo += f" password={password}"

        # Create pool if requested
        pool = None
        if pool_size is not None:
            pool = AsyncConnectionPool(
                conninfo,
                min_size=min_size or 5,
                max_size=pool_size,
                open=False,
            )
            await pool.open()

        adapter = cls(conninfo, pool)

        # Initialize schema if requested
        if init_schema:
            from cheap.db.postgres.schema import PostgresSchema

            async with adapter.connection() as conn:
                await PostgresSchema.create_schema(conn, include_audit=include_audit)

        return adapter

    async def connection(self) -> psycopg.AsyncConnection[TupleRow]:
        """
        Get a database connection (from pool if available).

        Returns:
            Async context manager for database connection.

        Example:
            ```python
            async with adapter.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
            ```
        """
        if self._pool is not None:
            # Get connection from pool
            return self._pool.connection()
        else:
            # Create standalone connection if not pooled
            if self._standalone_conn is None:
                self._standalone_conn = await psycopg.AsyncConnection.connect(self._conninfo)
                # Set timezone to UTC
                async with self._standalone_conn.cursor() as cur:
                    await cur.execute("SET TIME ZONE 'UTC'")
            return self._standalone_conn

    async def get_connection(self) -> psycopg.AsyncConnection[TupleRow]:
        """
        Get a raw connection (not a context manager).

        For use with DAO operations that manage their own connection lifecycle.

        Returns:
            Active database connection.
        """
        if self._pool is not None:
            # Get connection from pool
            conn = await self._pool.getconn()
            # Set timezone to UTC
            async with conn.cursor() as cur:
                await cur.execute("SET TIME ZONE 'UTC'")
            return conn
        else:
            # Use standalone connection
            if self._standalone_conn is None:
                self._standalone_conn = await psycopg.AsyncConnection.connect(self._conninfo)
                # Set timezone to UTC
                async with self._standalone_conn.cursor() as cur:
                    await cur.execute("SET TIME ZONE 'UTC'")
            return self._standalone_conn

    async def return_connection(self, conn: psycopg.AsyncConnection[TupleRow]) -> None:
        """
        Return a connection to the pool.

        Args:
            conn: Connection to return.
        """
        if self._pool is not None:
            await self._pool.putconn(conn)

    async def close(self) -> None:
        """Close all connections and pool."""
        if self._pool is not None:
            await self._pool.close()
        if self._standalone_conn is not None:
            await self._standalone_conn.close()
            self._standalone_conn = None

    @property
    def conninfo(self) -> str:
        """Get the connection string."""
        return self._conninfo

    @property
    def has_pool(self) -> bool:
        """Check if using connection pooling."""
        return self._pool is not None

    @property
    def is_connected(self) -> bool:
        """Check if currently connected."""
        if self._pool is not None:
            return not self._pool.closed
        return self._standalone_conn is not None

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        # Already opened in create()
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
        pool_status = "pooled" if self.has_pool else "standalone"
        return f"PostgresAdapter(conninfo={self._conninfo!r}, {pool_status}, {status})"
