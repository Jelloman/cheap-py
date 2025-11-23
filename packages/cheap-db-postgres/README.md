# cheap-db-postgres

PostgreSQL persistence module for the Cheap data model.

## Overview

This module provides PostgreSQL-based storage for CHEAP data model objects with async support using psycopg3.

## Features

- **Async PostgreSQL Support**: Uses psycopg3 for non-blocking database operations
- **Complete Schema**: Full implementation of CHEAP data model tables with PostgreSQL-specific types
- **Connection Pooling**: Built-in connection pool management for production deployments
- **Type Mapping**: Automatic mapping between PropertyType and PostgreSQL column types
- **PostgreSQL-Specific Features**:
  - Native UUID type support
  - TIMESTAMP WITH TIME ZONE for temporal data
  - Trigger-based audit tracking
  - MVCC for high concurrency
  - JSONB and array type support
- **Type Safe**: Full type hints with basedpyright compatibility

## Usage

### Creating a Connection

```python
from cheap.db.postgres import PostgresAdapter

# Production database with connection pooling
adapter = await PostgresAdapter.create(
    host="localhost",
    port=5432,
    dbname="cheap",
    user="cheap_user",
    password="password",
    pool_size=10,  # Max connections
)
```

### Saving a Catalog

```python
from cheap.core import CatalogImpl
from cheap.db.postgres import PostgresDao

catalog = CatalogImpl(...)
dao = PostgresDao(adapter)

await dao.save_catalog(catalog)
```

### Loading a Catalog

```python
catalog = await dao.load_catalog(catalog_id)
```

## Database Schema

The module creates 30+ tables including:
- Catalog metadata (catalog, catalog_def)
- Aspect definitions (aspect_def, property_def)
- Hierarchy definitions (hierarchy_def)
- Entity data (entity, aspect, property_value)
- Hierarchy content (5 specialized tables for different hierarchy types)
- Audit tracking (automatic with triggers)

## PostgreSQL-Specific Features

### Native UUID Type
Uses PostgreSQL's native UUID type for better performance and storage efficiency.

### Timezone Awareness
All connections automatically set timezone to UTC for consistent datetime handling.

### Audit Triggers
Automatic `created_at` and `updated_at` timestamp tracking via database triggers.

### MVCC Concurrency
Superior concurrent access patterns compared to file-based databases.

## Database Setup

```sql
CREATE DATABASE cheap;
CREATE USER cheap_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cheap TO cheap_user;
```

Then use the schema module to initialize tables:

```python
from cheap.db.postgres import PostgresSchema

await PostgresSchema.create_schema(adapter, include_audit=True)
```

## Dependencies

- cheap-core: Core CHEAP data model
- cheap-json: JSON serialization
- psycopg[binary,pool] >= 3.2.0: Modern async PostgreSQL driver with connection pooling

## Production Recommendations

- Use connection pooling (pool_size=10, min_size=5)
- Enable audit tracking for compliance
- Configure appropriate timeout settings
- Use EXPLAIN ANALYZE for query optimization
- Run VACUUM ANALYZE periodically for statistics

## License

MIT
