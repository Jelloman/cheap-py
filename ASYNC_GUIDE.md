# Async Programming Guide for CheapPy

Complete guide to async/await patterns in the CheapPy data caching system.

## Overview

CheapPy is built with **async-first architecture** throughout the entire stack:

- ✅ **Database operations** - All I/O is async (aiosqlite, asyncpg, aiomysql)
- ✅ **REST API** - FastAPI with native async support
- ✅ **REST Client** - Both async and sync clients available
- ✅ **Integration tests** - pytest-asyncio for async test support

This guide covers async usage patterns, best practices, and common pitfalls.

---

## Table of Contents

1. [Why Async?](#why-async)
2. [Database Operations](#database-operations)
3. [REST API](#rest-api)
4. [REST Client](#rest-client)
5. [Best Practices](#best-practices)
6. [Common Patterns](#common-patterns)
7. [Testing Async Code](#testing-async-code)
8. [Performance Tips](#performance-tips)
9. [Troubleshooting](#troubleshooting)

---

## Why Async?

### Benefits of Async in CheapPy

1. **I/O Efficiency**: Database and network operations don't block the event loop
2. **Concurrency**: Handle multiple requests simultaneously without threading overhead
3. **Scalability**: FastAPI can handle thousands of concurrent requests
4. **Resource Efficiency**: Lower memory usage compared to thread-per-request models

### When to Use Async vs Sync

**Use Async When:**
- Building web services or APIs
- High-concurrency workloads
- I/O-bound operations (database, network, file I/O)
- Modern Python 3.11+ applications

**Use Sync When:**
- Simple scripts or CLIs
- CPU-bound operations
- Legacy codebases without async support
- Rapid prototyping

---

## Database Operations

All database modules provide **async-only** APIs for optimal performance.

### SQLite (cheap-db-sqlite)

```python
import asyncio
from cheap.db.sqlite import SqliteAdapter, SqliteDao
from cheap.core import CatalogImpl, CatalogSpecies

async def main():
    # Create adapter with schema initialization
    adapter = await SqliteAdapter.create(
        "data/catalog.db",
        init_schema=True
    )

    # Create DAO
    dao = SqliteDao(adapter)

    # All database operations are async
    catalog = CatalogImpl(
        species=CatalogSpecies.SOURCE,
        version="1.0.0"
    )

    # Save catalog (async)
    await dao.save_catalog(catalog)

    # Load catalog (async)
    loaded = await dao.load_catalog(catalog.global_id)
    print(f"Loaded: {loaded.species}")

    # Always close adapter
    await adapter.close()

# Run async code
asyncio.run(main())
```

#### Using Context Managers

```python
async def main():
    # Adapter auto-closes with context manager
    adapter = await SqliteAdapter.create(":memory:", init_schema=True)
    async with adapter:
        dao = SqliteDao(adapter)
        catalog = CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0")
        await dao.save_catalog(catalog)
        loaded = await dao.load_catalog(catalog.global_id)
        print(f"Saved and loaded: {loaded.global_id}")

asyncio.run(main())
```

### PostgreSQL (cheap-db-postgres)

```python
from cheap.db.postgres import PostgresAdapter, PostgresDao

async def main():
    # Create adapter with connection pool
    adapter = await PostgresAdapter.create(
        host="localhost",
        port=5432,
        dbname="cheap_db",
        user="cheap_user",
        password="secret",
        init_schema=True,
        pool_min_size=1,
        pool_max_size=10  # Connection pool for concurrency
    )

    dao = PostgresDao(adapter)

    # Same async API as SQLite
    catalog = CatalogImpl(species=CatalogSpecies.CACHE, version="2.0.0")
    await dao.save_catalog(catalog)
    loaded = await dao.load_catalog(catalog.global_id)

    # Close pool and connections
    await adapter.close()

asyncio.run(main())
```

### MariaDB (cheap-db-mariadb)

```python
from cheap.db.mariadb import MariaDbAdapter, MariaDbDao

async def main():
    # MariaDB with connection pooling
    adapter = await MariaDbAdapter.create(
        host="localhost",
        port=3306,
        database="cheap_db",
        user="cheap_user",
        password="secret",
        init_schema=True,
        pool_min_size=1,
        pool_max_size=10
    )

    dao = MariaDbDao(adapter)

    # Identical async API across all databases
    catalog = CatalogImpl(species=CatalogSpecies.MIRROR, version="1.0.0")
    await dao.save_catalog(catalog)

    await adapter.close()

asyncio.run(main())
```

---

## REST API

The FastAPI-based REST API is **fully async** with native async endpoint support.

### Async Endpoints

All endpoints in `cheap.rest` are async:

```python
from fastapi import FastAPI, Depends
from typing import Annotated
from uuid import UUID

from cheap.db.sqlite import SqliteDao, get_dao
from cheap.core import Catalog

app = FastAPI()

@app.get("/api/catalog/{catalog_id}")
async def get_catalog(
    catalog_id: UUID,
    dao: Annotated[SqliteDao, Depends(get_dao)]
) -> Catalog:
    """Get catalog by ID - async endpoint."""
    return await dao.load_catalog(catalog_id)

@app.post("/api/catalog")
async def create_catalog(
    catalog: Catalog,
    dao: Annotated[SqliteDao, Depends(get_dao)]
) -> Catalog:
    """Create catalog - async endpoint."""
    await dao.save_catalog(catalog)
    return catalog
```

### Dependency Injection

FastAPI handles async dependencies automatically:

```python
from cheap.db.sqlite import SqliteAdapter, SqliteDao

# Global adapter (created at startup)
_adapter: SqliteAdapter | None = None

async def get_dao() -> SqliteDao:
    """Dependency that provides DAO instance."""
    global _adapter
    if _adapter is None:
        _adapter = await SqliteAdapter.create(":memory:", init_schema=True)
    return SqliteDao(_adapter)
```

### Lifespan Management

Use FastAPI lifespan for async resource management:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup: create database adapter
    adapter = await SqliteAdapter.create("data/catalog.db", init_schema=True)
    app.state.adapter = adapter

    yield  # Application runs

    # Shutdown: close database adapter
    await adapter.close()

app = FastAPI(lifespan=lifespan)
```

---

## REST Client

The REST client provides **both async and sync** interfaces.

### AsyncCheapClient (Recommended)

Use the async client for modern async applications:

```python
import asyncio
from cheap.rest.client import AsyncCheapClient
from cheap.core import CatalogSpecies

async def main():
    # Create async client with context manager
    async with AsyncCheapClient("http://localhost:8000") as client:
        # All operations are async
        catalog = await client.create_catalog(
            species=CatalogSpecies.SOURCE,
            version="1.0.0"
        )
        print(f"Created: {catalog.catalog_id}")

        # Get catalog
        loaded = await client.get_catalog(catalog.catalog_id)
        print(f"Loaded: {loaded.species}")

        # Delete catalog
        await client.delete_catalog(catalog.catalog_id)

        # Health check
        health = await client.health_check()
        print(f"Status: {health['status']}")

asyncio.run(main())
```

### Concurrent Operations

Async client enables concurrent requests:

```python
import asyncio
from cheap.rest.client import AsyncCheapClient
from cheap.core import CatalogSpecies

async def create_catalog(client: AsyncCheapClient, species: str):
    """Create a single catalog."""
    catalog = await client.create_catalog(
        species=CatalogSpecies(species),
        version="1.0.0"
    )
    print(f"Created {species}: {catalog.catalog_id}")
    return catalog

async def main():
    async with AsyncCheapClient("http://localhost:8000") as client:
        # Create 5 catalogs concurrently
        catalogs = await asyncio.gather(
            create_catalog(client, "SOURCE"),
            create_catalog(client, "SINK"),
            create_catalog(client, "CACHE"),
            create_catalog(client, "MIRROR"),
            create_catalog(client, "FORK"),
        )
        print(f"Created {len(catalogs)} catalogs concurrently")

asyncio.run(main())
```

### CheapClient (Synchronous)

Use the sync client for scripts and non-async code:

```python
from cheap.rest.client import CheapClient
from cheap.core import CatalogSpecies

# Synchronous API (no async/await)
with CheapClient("http://localhost:8000") as client:
    catalog = client.create_catalog(
        species=CatalogSpecies.SOURCE,
        version="1.0.0"
    )
    print(f"Created: {catalog.catalog_id}")

    loaded = client.get_catalog(catalog.catalog_id)
    print(f"Loaded: {loaded.species}")
```

**Note**: The sync client internally uses `httpx.Client` (not async), making it suitable for non-async environments.

---

## Best Practices

### 1. Always Use `asyncio.run()` for Entry Points

```python
import asyncio

async def main():
    """Main application logic."""
    # Your async code here
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Use Context Managers for Resource Management

```python
# Good: Auto-cleanup with context managers
async with AsyncCheapClient("http://localhost:8000") as client:
    await client.create_catalog(...)

# Bad: Manual cleanup (error-prone)
client = AsyncCheapClient("http://localhost:8000")
await client.create_catalog(...)
await client.close()  # Might not be called if error occurs
```

### 3. Concurrent Operations with `asyncio.gather()`

```python
# Run multiple operations concurrently
results = await asyncio.gather(
    dao.load_catalog(id1),
    dao.load_catalog(id2),
    dao.load_catalog(id3),
)

# With error handling
results = await asyncio.gather(
    dao.load_catalog(id1),
    dao.load_catalog(id2),
    return_exceptions=True  # Don't fail all if one fails
)
```

### 4. Sequential Operations with Dependencies

```python
# When operations depend on each other, run sequentially
catalog = await dao.load_catalog(catalog_id)
catalog.version = "2.0.0"
await dao.save_catalog(catalog)  # Wait for previous operation
loaded = await dao.load_catalog(catalog_id)  # Verify update
```

### 5. Error Handling in Async Code

```python
from cheap.rest.client.exceptions import CheapRestNotFoundException

async def safe_get_catalog(client, catalog_id):
    """Get catalog with error handling."""
    try:
        return await client.get_catalog(catalog_id)
    except CheapRestNotFoundException:
        print(f"Catalog {catalog_id} not found")
        return None
    except Exception as e:
        print(f"Error: {e}")
        raise
```

### 6. Timeouts for Long Operations

```python
import asyncio

# Set timeout for operation
try:
    catalog = await asyncio.wait_for(
        dao.load_catalog(catalog_id),
        timeout=5.0  # 5 seconds
    )
except asyncio.TimeoutError:
    print("Operation timed out")
```

---

## Common Patterns

### Pattern 1: Batch Processing

```python
async def batch_save_catalogs(dao: SqliteDao, catalogs: list[Catalog]):
    """Save multiple catalogs concurrently."""
    await asyncio.gather(*[
        dao.save_catalog(catalog)
        for catalog in catalogs
    ])

# Usage
catalogs = [
    CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0"),
    CatalogImpl(species=CatalogSpecies.SINK, version="1.0.0"),
    CatalogImpl(species=CatalogSpecies.CACHE, version="1.0.0"),
]
await batch_save_catalogs(dao, catalogs)
```

### Pattern 2: Background Tasks

```python
from fastapi import BackgroundTasks

async def cleanup_catalog(catalog_id: UUID, dao: SqliteDao):
    """Background task to clean up catalog."""
    await asyncio.sleep(60)  # Wait 60 seconds
    await dao.delete_catalog(catalog_id)

@app.delete("/api/catalog/{catalog_id}")
async def delete_catalog_deferred(
    catalog_id: UUID,
    background_tasks: BackgroundTasks,
    dao: Annotated[SqliteDao, Depends(get_dao)]
):
    """Delete catalog in background."""
    background_tasks.add_task(cleanup_catalog, catalog_id, dao)
    return {"status": "deletion scheduled"}
```

### Pattern 3: Streaming Responses

```python
from fastapi.responses import StreamingResponse

async def stream_catalogs(dao: SqliteDao):
    """Stream catalogs as JSON lines."""
    # Yield catalogs one by one
    for catalog_id in await dao.list_catalog_ids():
        catalog = await dao.load_catalog(catalog_id)
        yield f"{catalog.json()}\n"

@app.get("/api/catalogs/stream")
async def stream_all_catalogs(dao: Annotated[SqliteDao, Depends(get_dao)]):
    """Stream all catalogs."""
    return StreamingResponse(
        stream_catalogs(dao),
        media_type="application/x-ndjson"
    )
```

### Pattern 4: Async Generators

```python
async def fetch_catalogs_paginated(
    dao: SqliteDao,
    page_size: int = 10
):
    """Async generator for paginated catalog loading."""
    offset = 0
    while True:
        catalogs = await dao.load_catalogs_page(offset, page_size)
        if not catalogs:
            break
        for catalog in catalogs:
            yield catalog
        offset += page_size

# Usage
async for catalog in fetch_catalogs_paginated(dao):
    print(f"Processing: {catalog.global_id}")
```

---

## Testing Async Code

### pytest-asyncio

All async tests use `pytest-asyncio` for async test support:

```python
import pytest
import pytest_asyncio
from cheap.db.sqlite import SqliteAdapter, SqliteDao
from cheap.core import CatalogImpl, CatalogSpecies

@pytest_asyncio.fixture
async def dao():
    """Create SQLite DAO for testing."""
    adapter = await SqliteAdapter.create(":memory:", init_schema=True)
    dao = SqliteDao(adapter)
    yield dao
    await adapter.close()

@pytest.mark.asyncio
async def test_save_and_load_catalog(dao):
    """Test async catalog save/load."""
    catalog = CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0")

    # Async operations in tests
    await dao.save_catalog(catalog)
    loaded = await dao.load_catalog(catalog.global_id)

    assert loaded.global_id == catalog.global_id
    assert loaded.species == catalog.species
```

### Testing FastAPI Endpoints

```python
from httpx import ASGITransport, AsyncClient
from cheap.rest.main import create_app

@pytest.mark.asyncio
async def test_create_catalog_endpoint():
    """Test REST API endpoint."""
    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/catalog",
            json={"species": "SOURCE", "version": "1.0.0"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["species"] == "SOURCE"
```

### Testing Concurrent Operations

```python
@pytest.mark.asyncio
async def test_concurrent_catalog_operations(dao):
    """Test concurrent database operations."""
    # Create catalogs concurrently
    catalogs = [
        CatalogImpl(species=CatalogSpecies.SOURCE, version=f"{i}.0.0")
        for i in range(10)
    ]

    await asyncio.gather(*[
        dao.save_catalog(catalog)
        for catalog in catalogs
    ])

    # Verify all saved
    for catalog in catalogs:
        loaded = await dao.load_catalog(catalog.global_id)
        assert loaded.version == catalog.version
```

---

## Performance Tips

### 1. Connection Pooling

Configure appropriate pool sizes for your workload:

```python
# PostgreSQL with optimized pool
adapter = await PostgresAdapter.create(
    host="localhost",
    dbname="cheap_db",
    user="cheap_user",
    password="secret",
    pool_min_size=5,      # Minimum connections
    pool_max_size=20,     # Maximum connections
    pool_max_idle=60.0,   # Idle timeout
)
```

### 2. Batch Operations

Use `asyncio.gather()` for concurrent operations:

```python
# Good: Concurrent (fast)
await asyncio.gather(*[
    dao.save_catalog(catalog)
    for catalog in catalogs
])

# Bad: Sequential (slow)
for catalog in catalogs:
    await dao.save_catalog(catalog)
```

### 3. Limit Concurrency

Use `asyncio.Semaphore` to limit concurrent operations:

```python
async def save_with_limit(dao, catalogs, max_concurrent=10):
    """Save catalogs with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def save_one(catalog):
        async with semaphore:
            await dao.save_catalog(catalog)

    await asyncio.gather(*[save_one(c) for c in catalogs])
```

### 4. Use httpx Connection Pooling

```python
from cheap.rest.client import AsyncCheapClient, CheapClientConfig

# Configure client with connection pool
config = CheapClientConfig(
    base_url="http://localhost:8000",
    max_connections=100,
    max_keepalive_connections=20
)
async with AsyncCheapClient(config=config) as client:
    # Reuses connections efficiently
    await client.create_catalog(...)
```

---

## Troubleshooting

### Common Issues

#### 1. RuntimeError: Event loop is closed

**Problem:**
```python
asyncio.run(main())
asyncio.run(main())  # Error: event loop already closed
```

**Solution:**
```python
# Create new event loop if needed
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.close()
```

#### 2. Task was destroyed but it is pending

**Problem:** Not awaiting all tasks before shutdown.

**Solution:**
```python
# Cancel pending tasks on shutdown
async def cleanup():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
```

#### 3. Too many open files

**Problem:** Not closing database connections.

**Solution:**
```python
# Always use context managers or close explicitly
async with await SqliteAdapter.create(...) as adapter:
    # Use adapter
    pass  # Auto-closed
```

#### 4. Blocking the event loop

**Problem:** CPU-bound operations blocking async I/O.

**Solution:**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def cpu_bound_async(data):
    """Run CPU-bound work in thread pool."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_bound_function, data)
    return result
```

---

## Summary

CheapPy's async-first architecture provides:

- ✅ **High performance** - Non-blocking I/O throughout
- ✅ **Scalability** - Handle thousands of concurrent operations
- ✅ **Flexibility** - Both async and sync clients available
- ✅ **Best practices** - Context managers, connection pooling, error handling

For optimal performance, use async APIs throughout your application stack. The sync client is available for gradual migration or integration with legacy code.

---

## Further Reading

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [FastAPI async documentation](https://fastapi.tiangolo.com/async/)
- [httpx async client](https://www.python-httpx.org/async/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [aiosqlite](https://aiosqlite.omnilib.dev/)
- [asyncpg](https://magicstack.github.io/asyncpg/)
