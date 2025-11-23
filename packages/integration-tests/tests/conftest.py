"""Shared test fixtures for integration tests."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
import pytest_asyncio
from cheap.core.catalog_impl import CatalogImpl
from cheap.core.catalog_species import CatalogSpecies
from cheap.db.sqlite.adapter import SqliteAdapter
from cheap.db.sqlite.dao import SqliteDao

if TYPE_CHECKING:
    from cheap.core.catalog import Catalog


@pytest_asyncio.fixture
async def sqlite_dao() -> AsyncGenerator[SqliteDao, None]:
    """Create a SQLite DAO with in-memory database."""
    adapter = await SqliteAdapter.create(
        ":memory:",
        init_schema=True,
    )
    dao = SqliteDao(adapter)
    yield dao
    await adapter.close()


@pytest_asyncio.fixture
async def postgres_dao() -> AsyncGenerator[object, None]:
    """Create a PostgreSQL DAO (requires PostgreSQL server)."""
    # Skip if PostgreSQL not available
    if not os.getenv("POSTGRES_AVAILABLE"):
        pytest.skip("PostgreSQL not available (set POSTGRES_AVAILABLE=1 to enable)")

    from cheap.db.postgres.adapter import PostgresAdapter
    from cheap.db.postgres.dao import PostgresDao

    adapter = await PostgresAdapter.create(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "cheap_test"),
        user=os.getenv("POSTGRES_USER", "cheap_user"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        init_schema=True,
    )
    dao = PostgresDao(adapter)
    yield dao
    await adapter.close()


@pytest_asyncio.fixture
async def mariadb_dao() -> AsyncGenerator[object, None]:
    """Create a MariaDB DAO (requires MariaDB server)."""
    # Skip if MariaDB not available
    if not os.getenv("MARIADB_AVAILABLE"):
        pytest.skip("MariaDB not available (set MARIADB_AVAILABLE=1 to enable)")

    from cheap.db.mariadb.adapter import MariaDbAdapter
    from cheap.db.mariadb.dao import MariaDbDao

    adapter = await MariaDbAdapter.create(
        host=os.getenv("MARIADB_HOST", "localhost"),
        port=int(os.getenv("MARIADB_PORT", "3306")),
        database=os.getenv("MARIADB_DB", "cheap_test"),
        user=os.getenv("MARIADB_USER", "cheap_user"),
        password=os.getenv("MARIADB_PASSWORD", ""),
        init_schema=True,
    )
    dao = MariaDbDao(adapter)
    yield dao
    await adapter.close()


@pytest.fixture
def sample_catalog() -> Catalog:
    """Create a sample catalog for testing."""
    return CatalogImpl(
        global_id=uuid4(),
        species=CatalogSpecies.SOURCE,
        version="1.0.0",
    )
