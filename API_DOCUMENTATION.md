# CheapPy API Documentation

Comprehensive API reference for all 8 modules in the CheapPy data caching system.

## Table of Contents

- [cheap-core](#cheap-core) - Core CHEAP model
- [cheap-json](#cheap-json) - JSON serialization
- [cheap-db-sqlite](#cheap-db-sqlite) - SQLite persistence
- [cheap-db-postgres](#cheap-db-postgres) - PostgreSQL persistence
- [cheap-db-mariadb](#cheap-db-mariadb) - MariaDB persistence
- [cheap-rest](#cheap-rest) - REST API
- [cheap-rest-client](#cheap-rest-client) - REST client
- [integration-tests](#integration-tests) - Integration tests

**Note**: CheapPy uses async-first architecture throughout. See **[ASYNC_GUIDE.md](ASYNC_GUIDE.md)** for comprehensive async programming patterns and best practices.

---

## cheap-core

Core CHEAP model with protocols, implementations, and utilities.

### Key Modules

#### Protocols (`cheap.core.*`)

Core Protocol interfaces define the CHEAP model structure:

- **`Catalog`**: Container for entities and hierarchies
- **`Entity`**: Core data object with global/local IDs
- **`Aspect`**: Named group of properties
- **`Property`**: Individual typed data value
- **`Hierarchy`**: Organizational structure (List, Set, Directory, Tree, AspectMap)
- **`AspectDef`**: Property schema definition
- **`PropertyDef`**: Individual property schema

All protocols are runtime-checkable for type validation.

#### Implementations (`cheap.core.*_impl`)

Concrete implementations of CHEAP protocols:

```python
from cheap.core import CatalogImpl, EntityImpl, AspectImpl, PropertyImpl

# Create catalog
catalog = CatalogImpl(
    species=CatalogSpecies.SOURCE,
    version="1.0.0",
    global_id=uuid4()  # Optional, auto-generated
)

# Create entity
entity = EntityImpl(
    id=uuid4(),  # Optional, auto-generated
    local_id=12345  # Optional
)

# Create aspect with properties
aspect = AspectImpl(
    entity_id=entity.id,
    aspect_name="person",
    properties={
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com"
    }
)

# Add aspect to entity
entity.aspects["person"] = aspect
```

#### Enums

**`CatalogSpecies`** (StrEnum):
- `SOURCE`: Source of truth catalog
- `SINK`: Data sink catalog
- `CACHE`: Cached data catalog
- `MIRROR`: Mirror/replica catalog
- `FORK`: Forked catalog

**`HierarchyType`** (StrEnum):
- `LIST`: Ordered sequence
- `SET`: Unordered unique collection
- `DIRECTORY`: Key-value mapping
- `TREE`: Hierarchical parent-child
- `ASPECT_MAP`: Entity-to-aspect mapping

**`PropertyType`** (StrEnum):
- Numeric: `INTEGER`, `FLOAT`, `BIG_INTEGER`, `BIG_DECIMAL`
- String: `STRING`, `TEXT`
- Other: `BOOLEAN`, `DATE_TIME`, `URI`, `UUID`
- Binary: `CLOB`, `BLOB`

#### Utilities

**`CheapHasher`**: Cryptographic hashing utilities
```python
from cheap.core import CheapHasher

# Hash a catalog
hash_value = CheapHasher.hash_catalog(catalog)

# Hash an entity
hash_value = CheapHasher.hash_entity(entity)
```

**`CheapFactory`**: Factory for creating CHEAP objects
```python
from cheap.core import CheapFactory

# Create catalog
catalog = CheapFactory.create_catalog(
    species=CatalogSpecies.SOURCE,
    version="1.0.0"
)

# Create entity
entity = CheapFactory.create_entity()
```

---

## cheap-json

High-performance JSON serialization using orjson.

### Core Classes

#### `CheapJSONSerializer`

Serialize/deserialize CHEAP objects to/from JSON with native type support.

```python
from cheap.json import CheapJSONSerializer
from cheap.core import CatalogImpl, CatalogSpecies

# Create serializer
serializer = CheapJSONSerializer()

# Serialize catalog to JSON string
catalog = CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0")
json_str = serializer.serialize_catalog(catalog)

# Deserialize catalog from JSON string
loaded_catalog = serializer.deserialize_catalog(json_str)

# Serialize to file
with open("catalog.json", "wb") as f:
    serializer.serialize_catalog_to_file(catalog, f)

# Deserialize from file
with open("catalog.json", "rb") as f:
    loaded_catalog = serializer.deserialize_catalog_from_file(f)
```

**Key Features:**
- Native UUID, datetime, Decimal support (no string conversion)
- 2-3x faster than stdlib json module
- Type preservation for CHEAP objects
- Streaming support for large datasets

---

## cheap-db-sqlite

SQLite database persistence with async support.

### Core Classes

#### `SqliteAdapter`

Low-level SQLite database connection management.

```python
from cheap.db.sqlite import SqliteAdapter

# Create adapter with schema initialization
adapter = await SqliteAdapter.create(
    "data/catalog.db",
    init_schema=True,      # Initialize database schema
    include_audit=False    # Optional audit tables
)

# Get connection
conn = await adapter.get_connection()

# Close connection
await adapter.close()
```

#### `SqliteDao`

High-level data access object for catalog operations.

```python
from cheap.db.sqlite import SqliteAdapter, SqliteDao
from cheap.core import CatalogImpl, CatalogSpecies

# Create DAO
adapter = await SqliteAdapter.create(":memory:", init_schema=True)
dao = SqliteDao(adapter)

# Save catalog
catalog = CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0")
await dao.save_catalog(catalog)

# Load catalog
loaded = await dao.load_catalog(catalog.global_id)

# Delete catalog
await dao.delete_catalog(catalog.global_id)

# Check if catalog exists
exists = await dao.catalog_exists(catalog.global_id)
```

**Schema Management:**
- 17 tables for complete CHEAP model
- Foreign key constraints
- Indexes for performance
- Transaction support

---

## cheap-db-postgres

PostgreSQL database persistence with async support.

### Core Classes

#### `PostgresAdapter`

PostgreSQL connection management with pooling.

```python
from cheap.db.postgres import PostgresAdapter

# Create adapter
adapter = await PostgresAdapter.create(
    host="localhost",
    port=5432,
    dbname="cheap_db",
    user="cheap_user",
    password="secret",
    init_schema=True,
    pool_min_size=1,
    pool_max_size=10
)

# Get connection
conn = await adapter.get_connection()

# Close connection and pool
await adapter.close()
```

#### `PostgresDao`

Data access object for PostgreSQL.

```python
from cheap.db.postgres import PostgresAdapter, PostgresDao

# Create DAO
adapter = await PostgresAdapter.create(
    host="localhost",
    dbname="cheap_db",
    user="cheap_user",
    password="secret",
    init_schema=True
)
dao = PostgresDao(adapter)

# Same API as SqliteDao
await dao.save_catalog(catalog)
loaded = await dao.load_catalog(catalog.global_id)
```

**Advanced Features:**
- Connection pooling with asyncpg
- JSONB for flexible property storage
- Array types for collections
- Full transaction support

---

## cheap-db-mariadb

MariaDB/MySQL database persistence with async support.

### Core Classes

#### `MariaDbAdapter`

MariaDB connection management with pooling.

```python
from cheap.db.mariadb import MariaDbAdapter

# Create adapter
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

# Get connection
conn = await adapter.get_connection()

# Close connection and pool
await adapter.close()
```

#### `MariaDbDao`

Data access object for MariaDB.

```python
from cheap.db.mariadb import MariaDbAdapter, MariaDbDao

# Create DAO
adapter = await MariaDbAdapter.create(
    host="localhost",
    database="cheap_db",
    user="cheap_user",
    password="secret",
    init_schema=True
)
dao = MariaDbDao(adapter)

# Same API as SqliteDao
await dao.save_catalog(catalog)
loaded = await dao.load_catalog(catalog.global_id)
```

**Compatibility:**
- MySQL 8.0+
- MariaDB 10.5+
- UTF-8 character set support
- Connection pooling with aiomysql

---

## cheap-rest

FastAPI-based REST API with multi-database backend support.

### REST Endpoints

#### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "sqlite"
}
```

#### Create Catalog

```http
POST /api/catalog
Content-Type: application/json

{
  "species": "SOURCE",
  "version": "1.0.0"
}
```

Response (201 Created):
```json
{
  "catalog_id": "550e8400-e29b-41d4-a716-446655440000",
  "species": "SOURCE",
  "version": "1.0.0",
  "created_at": "2025-11-23T10:00:00Z"
}
```

#### Get Catalog

```http
GET /api/catalog/{catalog_id}
```

Response (200 OK):
```json
{
  "catalog_id": "550e8400-e29b-41d4-a716-446655440000",
  "species": "SOURCE",
  "version": "1.0.0",
  "created_at": "2025-11-23T10:00:00Z"
}
```

#### Delete Catalog

```http
DELETE /api/catalog/{catalog_id}
```

Response: 204 No Content

### Running the API

```bash
# Development mode
uvicorn cheap.rest.main:app --reload

# Production mode
uvicorn cheap.rest.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Configuration

Environment variables:
- `CHEAP_DB_BACKEND`: Database backend (`sqlite`, `postgres`, `mariadb`)
- `CHEAP_DB_PATH`: SQLite database path
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `MARIADB_HOST`, `MARIADB_PORT`, `MARIADB_DB`, `MARIADB_USER`, `MARIADB_PASSWORD`

### OpenAPI Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## cheap-rest-client

Python client library for the CHEAP REST API.

### Core Classes

#### `AsyncCheapClient`

Async client for CHEAP REST API.

```python
from cheap.rest.client import AsyncCheapClient
from cheap.core import CatalogSpecies

# Create client
async with AsyncCheapClient("http://localhost:8000") as client:
    # Create catalog
    catalog = await client.create_catalog(
        species=CatalogSpecies.SOURCE,
        version="1.0.0"
    )
    print(f"Created catalog: {catalog.catalog_id}")

    # Get catalog
    loaded = await client.get_catalog(catalog.catalog_id)
    print(f"Loaded catalog: {loaded.species}")

    # Delete catalog
    await client.delete_catalog(catalog.catalog_id)
    print("Catalog deleted")

    # Health check
    health = await client.health_check()
    print(f"API Status: {health['status']}")
```

#### `CheapClient` (Synchronous)

Synchronous client wrapper for non-async code.

**Usage:**
```python
from cheap.rest.client import CheapClient
from cheap.core import CatalogSpecies

# Synchronous API (no async/await)
with CheapClient("http://localhost:8000") as client:
    # Create catalog
    catalog = client.create_catalog(
        species=CatalogSpecies.SOURCE,
        version="1.0.0"
    )
    print(f"Created: {catalog.catalog_id}")

    # Get catalog
    loaded = client.get_catalog(catalog.catalog_id)
    print(f"Loaded: {loaded.species}")

    # Delete catalog
    client.delete_catalog(catalog.catalog_id)
```

**Note**: The synchronous client uses `httpx.Client` internally (not async), making it suitable for scripts and non-async environments. For modern async applications, use `AsyncCheapClient`.

**Features:**
- Type-safe request/response handling
- Automatic retry on transient failures
- Connection pooling
- Timeout configuration
- Custom exception hierarchy

---

## integration-tests

Comprehensive integration test suite.

### Test Suites

#### Cross-Database Tests

Verify consistency across SQLite, PostgreSQL, and MariaDB.

```python
import pytest
from cheap.db.sqlite import SqliteAdapter, SqliteDao

@pytest.mark.integration
@pytest.mark.database
async def test_save_and_load_catalog(sqlite_dao):
    """Test saving and loading a catalog."""
    await sqlite_dao.save_catalog(sample_catalog)
    loaded = await sqlite_dao.load_catalog(sample_catalog.global_id)
    assert loaded.species == sample_catalog.species
```

#### End-to-End API Tests

Test full REST API lifecycle.

```python
import pytest
from httpx import ASGITransport, AsyncClient
from cheap.rest.main import create_app

@pytest.mark.integration
@pytest.mark.e2e
async def test_create_and_get_catalog_e2e():
    """Test creating and retrieving a catalog through the API."""
    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create catalog
        response = await client.post(
            "/api/catalog",
            json={"species": "SOURCE", "version": "1.0.0"}
        )
        assert response.status_code == 201
```

#### REST Client Integration Tests

Test REST client with live API.

```python
@pytest.mark.integration
@pytest.mark.e2e
async def test_client_crud_cycle():
    """Test full CRUD cycle through the REST client."""
    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        # Create, Read, Delete operations
        ...
```

### Running Integration Tests

```bash
# Run all integration tests
uv run pytest packages/integration-tests/tests/ -v

# Run with markers
uv run pytest -m "integration and database"
uv run pytest -m "e2e"

# Run with coverage
uv run pytest packages/integration-tests/ --cov --cov-report=html
```

---

## Common Patterns

### Error Handling

All modules use custom exception hierarchies:

```python
from cheap.core.exceptions import CheapException, CatalogNotFoundException

try:
    catalog = await dao.load_catalog(catalog_id)
except CatalogNotFoundException:
    print("Catalog not found")
except CheapException as e:
    print(f"CHEAP error: {e}")
```

### Async Context Managers

Database adapters and clients use async context managers:

```python
# Adapter
async with await SqliteAdapter.create(":memory:") as adapter:
    dao = SqliteDao(adapter)
    # Use dao...
    # Adapter automatically closed

# Client
async with AsyncCheapClient("http://localhost:8000") as client:
    # Use client...
    # Client automatically closed
```

### Type Safety

All APIs are fully type-hinted with strict type checking:

```python
from cheap.core import Catalog, CatalogSpecies
from uuid import UUID

async def save_catalog(catalog: Catalog) -> None:
    """Save a catalog - type checked at compile time."""
    await dao.save_catalog(catalog)

async def load_catalog(catalog_id: UUID) -> Catalog:
    """Load a catalog - return type guaranteed."""
    return await dao.load_catalog(catalog_id)
```

---

## Migration from Java

### Key Differences

| Java Concept | Python Equivalent | Notes |
|--------------|------------------|-------|
| Interface + Impl | Protocol + Class | No inheritance required |
| `@Autowired` | FastAPI Depends | Dependency injection |
| `Optional<T>` | `T \| None` | Python 3.10+ union syntax |
| `UUID.randomUUID()` | `uuid.uuid4()` | Same functionality |
| `CompletableFuture` | `asyncio.Task` | Async/await pattern |
| `Stream<T>` | `AsyncIterator[T]` | Async generators |
| `@NotNull` | Type without None | Type system enforced |
| Lombok getters | `@property` | Python properties |

### Example Migration

**Java:**
```java
@Service
public class CatalogService {
    @Autowired
    private CatalogRepository repository;

    public CompletableFuture<Catalog> getCatalog(UUID id) {
        return repository.findById(id)
            .orElseThrow(() -> new CatalogNotFoundException(id));
    }
}
```

**Python:**
```python
from typing import Annotated
from fastapi import Depends
from cheap.db.sqlite import SqliteDao, get_dao

async def get_catalog(
    catalog_id: UUID,
    dao: Annotated[SqliteDao, Depends(get_dao)]
) -> Catalog:
    """Get catalog by ID."""
    try:
        return await dao.load_catalog(catalog_id)
    except ValueError:
        raise CatalogNotFoundException(catalog_id)
```

---

## Performance Tips

1. **Use async/await** - All I/O operations are async
2. **Connection pooling** - Configure pool sizes for your workload
3. **Batch operations** - Use transactions for multiple operations
4. **Index optimization** - Ensure proper database indexes
5. **orjson** - Already configured for fast JSON
6. **Caching** - Implement caching layer for read-heavy workloads

---

## Further Reading

- [README.md](README.md) - Project overview and quick start
- [CLAUDE.md](CLAUDE.md) - Development guide and commands
- [INITIAL_PLAN.md](INITIAL_PLAN.md) - Complete porting plan
- Package READMEs - Detailed package documentation
- [Java Source](https://github.com/Jelloman/cheap) - Original Java implementation
