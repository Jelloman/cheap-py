# cheap-db-mariadb

MariaDB/MySQL persistence module for the Cheap data model.

## Features

- **Async MariaDB/MySQL Support**: Built on aiomysql for non-blocking database operations
- **Connection Pooling**: Optional connection pooling for production deployments
- **UTF-8MB4 Support**: Full Unicode support including emojis and special characters
- **Audit Tracking**: Automatic timestamp tracking with `created_at` and `updated_at` columns
- **Foreign Key Support**: Optional referential integrity constraints
- **Compatible**: Works with both MariaDB and MySQL databases

## Installation

```bash
pip install cheap-db-mariadb
```

## Quick Start

### Basic Usage

```python
from cheap.db.mariadb.adapter import MariaDbAdapter
from cheap.db.mariadb.dao import MariaDbDao
from cheap.core.catalog_impl import CatalogImpl
from cheap.core.catalog_species import CatalogSpecies
from uuid import uuid4

# Create adapter with connection pooling
adapter = await MariaDbAdapter.create(
    host="localhost",
    port=3306,
    db="cheap",
    user="cheap_user",
    password="secret",
    pool_size=10,  # Enable connection pooling
    init_schema=True,  # Create schema on first connect
    include_audit=True,  # Include audit columns
)

# Create DAO
dao = MariaDbDao(adapter)

# Create and save a catalog
catalog = CatalogImpl(
    global_id=uuid4(),
    species=CatalogSpecies.SOURCE,
    version="1.0.0",
)
await dao.save_catalog(catalog)

# Load the catalog
loaded = await dao.load_catalog(catalog.global_id)

# Clean up
await adapter.close()
```

### Context Manager Support

```python
async with await MariaDbAdapter.create(
    host="localhost",
    port=3306,
    db="cheap",
    user="cheap_user",
    password="secret",
) as adapter:
    dao = MariaDbDao(adapter)
    # Use dao...
    # Adapter automatically closed on exit
```

## Schema Management

```python
from cheap.db.mariadb.schema import MariaDbSchema
from cheap.db.mariadb.adapter import MariaDbAdapter

async with await MariaDbAdapter.create(...) as adapter:
    conn = await adapter.get_connection()

    # Create schema
    await MariaDbSchema.create_schema(
        conn,
        include_audit=True,
        include_foreign_keys=True,
    )

    # Check if schema exists
    exists = await MariaDbSchema.schema_exists(conn)

    # Truncate all data (keep schema)
    await MariaDbSchema.truncate_data(conn)

    # Drop entire schema
    await MariaDbSchema.drop_schema(conn)

    await adapter.return_connection(conn)
```

## Configuration

### Connection Parameters

- **host**: MariaDB/MySQL server hostname (default: "localhost")
- **port**: Server port (default: 3306)
- **db**: Database name (default: "cheap")
- **user**: Database user (default: "cheap_user")
- **password**: Database password (default: "")
- **charset**: Character set (default: "utf8mb4")
- **pool_size**: Max connections in pool (None = no pooling)
- **min_size**: Minimum pool size (default: 5)
- **init_schema**: Create schema on connect (default: False)
- **include_audit**: Include audit columns (default: False)
- **include_foreign_keys**: Include FK constraints (default: False)

### Connection Pooling

For production deployments, enable connection pooling:

```python
adapter = await MariaDbAdapter.create(
    host="prod-mariadb.example.com",
    port=3306,
    db="cheap_prod",
    user="app_user",
    password=os.getenv("DB_PASSWORD"),
    pool_size=20,  # Maximum 20 connections
    min_size=5,    # Keep 5 connections warm
)
```

### Standalone Connection

For simpler use cases (development, testing), use standalone mode:

```python
adapter = await MariaDbAdapter.create(
    host="localhost",
    db="cheap_test",
    user="test_user",
    # No pool_size = standalone connection
)
```

## MariaDB vs MySQL Compatibility

This module works with both MariaDB and MySQL:

- **MariaDB 10.5+**: Recommended for production
- **MySQL 8.0+**: Fully supported
- **MySQL 5.7**: Supported with limitations (JSON type, audit features)

Key differences handled automatically:
- MariaDB-specific features (WAIT clause in TRUNCATE)
- MySQL compatibility mode for older versions
- Character set and collation defaults

## Database Schema

The schema includes 11 core tables:

### Definition Tables
- `aspect_def` - Aspect definitions with properties
- `property_def` - Property definitions with types

### Core Tables
- `catalog` - Top-level catalogs
- `hierarchy` - Hierarchy definitions
- `aspect` - Entity aspect instances
- `property_value` - Generic property value storage (EAV pattern)

### Hierarchy Content Tables
- `hierarchy_entity_list` - Ordered entity lists
- `hierarchy_entity_set` - Unique entity sets
- `hierarchy_entity_directory` - String-to-entity mappings
- `hierarchy_entity_tree_node` - Hierarchical tree structures
- `hierarchy_aspect_map` - Entity-to-aspect mappings

### Link Tables
- `catalog_aspect_def` - Catalog-to-aspect-definition links

## Type Mapping

PropertyType enum values map to MariaDB/MySQL types:

| PropertyType | MariaDB Type | Notes |
|---|---|---|
| INTEGER | BIGINT | 64-bit signed integer |
| FLOAT | DOUBLE | 64-bit floating point |
| BIG_INTEGER | BIGINT | Large integers |
| BIG_DECIMAL | DECIMAL | Precise decimals |
| BOOLEAN | BOOLEAN | True/false values |
| STRING | VARCHAR(8192) | Variable-length strings |
| TEXT | TEXT | Unlimited text |
| CLOB | LONGTEXT | Character large objects |
| BLOB | LONGBLOB | Binary large objects |
| DATE_TIME | VARCHAR(64) | ISO-8601 format |
| URI | VARCHAR(2048) | URI strings |
| UUID | CHAR(36) | Standard UUID format |

## Development

### Running Tests

```bash
# Set environment variables for test database
export MARIADB_AVAILABLE=1
export MARIADB_HOST=localhost
export MARIADB_PORT=3306
export MARIADB_DB=cheap_test
export MARIADB_USER=test_user
export MARIADB_PASSWORD=test_pass

# Run tests
pytest packages/cheap-db-mariadb/tests/ -v
```

Tests will be skipped if MariaDB is not available.

### Type Checking

```bash
basedpyright packages/cheap-db-mariadb/
```

### Formatting

```bash
ruff format packages/cheap-db-mariadb/
```

## License

MIT
