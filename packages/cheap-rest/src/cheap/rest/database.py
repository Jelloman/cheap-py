"""Database dependency provider."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from cheap.db.mariadb.adapter import MariaDbAdapter
from cheap.db.mariadb.dao import MariaDbDao
from cheap.db.postgres.adapter import PostgresAdapter
from cheap.db.postgres.dao import PostgresDao
from cheap.db.sqlite.adapter import SqliteAdapter
from cheap.db.sqlite.dao import SqliteDao
from cheap.rest.config import DatabaseType, settings

# Global DAO instance
_dao_instance: SqliteDao | PostgresDao | MariaDbDao | None = None


async def get_dao() -> AsyncGenerator[SqliteDao | PostgresDao | MariaDbDao, None]:
    """Get the configured DAO instance based on settings.

    Yields:
        DAO instance for the configured database backend
    """
    global _dao_instance

    if _dao_instance is None:
        # Initialize DAO based on configuration
        if settings.database_type == DatabaseType.SQLITE:
            adapter = await SqliteAdapter.create(
                db_path=settings.database_path,
                init_schema=True,
            )
            _dao_instance = SqliteDao(adapter)

        elif settings.database_type == DatabaseType.POSTGRES:
            adapter = await PostgresAdapter.create(
                host=settings.postgres_host,
                port=settings.postgres_port,
                dbname=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
                init_schema=True,
            )
            _dao_instance = PostgresDao(adapter)

        elif settings.database_type == DatabaseType.MARIADB:
            adapter = await MariaDbAdapter.create(
                host=settings.mariadb_host,
                port=settings.mariadb_port,
                db=settings.mariadb_db,
                user=settings.mariadb_user,
                password=settings.mariadb_password,
                init_schema=True,
            )
            _dao_instance = MariaDbDao(adapter)

    yield _dao_instance
