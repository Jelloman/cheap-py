# cheap-db-sqlite

SQLite persistence module for the Cheap data model.

## Overview

This module provides SQLite-based storage for CHEAP data model objects with async support using aiosqlite.

## Features

- **Async SQLite Support**: Uses aiosqlite for non-blocking database operations
- **Complete Schema**: Full implementation of CHEAP data model tables
- **Transaction Support**: All persistence operations wrapped in transactions
- **Type Mapping**: Automatic mapping between PropertyType and SQLite column types
- **In-Memory Mode**: Support for in-memory databases for testing
- **Type Safe**: Full type hints with basedpyright compatibility

## Usage

### Creating a Database

```python
from cheap.db.sqlite import SqliteAdapter, SqliteDao

# File-based database
adapter = await SqliteAdapter.create("path/to/database.db")

# In-memory database (for testing)
adapter = await SqliteAdapter.create(":memory:")
```

### Saving a Catalog

```python
from cheap.core import CatalogImpl
from cheap.db.sqlite import SqliteDao

catalog = CatalogImpl(...)
dao = SqliteDao(adapter)

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
- Audit tracking (optional)

## Dependencies

- cheap-core: Core CHEAP data model
- cheap-json: JSON serialization
- aiosqlite >= 0.19.0: Async SQLite driver

## License

MIT
