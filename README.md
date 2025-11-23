# CheapPy - Python Port of Cheap

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: basedpyright](https://img.shields.io/badge/type%20checked-basedpyright-blue.svg)](https://github.com/DetachHead/basedpyright)

A comprehensive Python implementation of the **CHEAP model** (Catalog, Hierarchy, Entity, Aspect, Property) - a git-like system for structured data caching and persistence.

This is a complete port of the [Java Cheap project](https://github.com/Jelloman/cheap), implementing all 8 modules with full type safety, async support, and multi-database backends.

## 🎯 What is CHEAP?

CHEAP is a data model for building flexible, version-controlled data systems similar to git, but for structured data. It provides:

- **Catalog**: Storage containers analogous to git repositories
- **Hierarchy**: Organizational structures (Lists, Sets, Directories, Trees, AspectMaps)
- **Entity**: Core data objects with unique identifiers
- **Aspect**: Named groups of related properties (like database tables/schemas)
- **Property**: Individual typed data values with full metadata

## 📦 Project Structure

This is a monorepo workspace containing 8 packages:

```
cheap-py/
├── pyproject.toml              # UV workspace root
├── noxfile.py                  # Multi-version testing
├── pyrightconfig.json          # Type checking config
├── packages/
│   ├── cheap-core/             # ✅ Core protocols & implementations
│   ├── cheap-json/             # ✅ JSON serialization (orjson)
│   ├── cheap-db-sqlite/        # ✅ SQLite persistence
│   ├── cheap-db-postgres/      # ✅ PostgreSQL persistence
│   ├── cheap-db-mariadb/       # ✅ MariaDB/MySQL persistence
│   ├── cheap-rest/             # ✅ FastAPI REST API
│   ├── cheap-rest-client/      # ✅ Python REST client
│   └── integration-tests/      # ✅ Cross-database integration tests
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) for fast dependency management
- (Optional) Docker for running PostgreSQL/MariaDB integration tests

### Installation

```bash
# Clone the repository
git clone https://github.com/Jelloman/cheap-py.git
cd cheap-py

# Install all dependencies and workspace packages
uv sync --extra dev

# Verify installation
uv run pytest packages/cheap-core/tests/ -v
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests across all packages
nox

# Run tests for specific Python version
nox -s tests-3.13

# Run integration tests
uv run pytest packages/integration-tests/tests/ -v

# Run tests with coverage
uv run pytest --cov=packages --cov-report=term-missing
```

### Code Quality

```bash
# Format code (REQUIRED before committing)
nox -s format

# Type checking
nox -s typecheck

# Linting
nox -s lint

# Run all quality checks
nox -s format typecheck lint
```

### Building Packages

```bash
# Build a specific package
cd packages/cheap-core
hatch build

# Build all packages
for pkg in packages/*/; do (cd "$pkg" && hatch build); done
```

## 📚 Package Overview

### cheap-core
Core CHEAP model with protocols, implementations, and utilities.

**Key Features:**
- Protocol-based architecture using structural typing
- 14+ implementation classes (CatalogImpl, EntityImpl, etc.)
- Type-safe property system with 11 data types
- Reflection-based implementations for dynamic catalogs
- Zero external dependencies (stdlib only)

**Usage:**
```python
from cheap.core import CatalogImpl, CatalogSpecies, EntityImpl, AspectImpl

# Create a catalog
catalog = CatalogImpl(species=CatalogSpecies.SOURCE, version="1.0.0")

# Create an entity with aspects
entity = EntityImpl()
entity.aspects["person"] = AspectImpl(
    entity_id=entity.id,
    aspect_name="person",
    properties={"name": "Alice", "age": 30}
)
```

### cheap-json
High-performance JSON serialization using orjson with native UUID/datetime support.

**Key Features:**
- Fast serialization/deserialization with orjson
- Native UUID, datetime, Decimal support
- Preserves type information for CHEAP objects
- Streaming support for large datasets

### cheap-db-sqlite
SQLite database persistence for development and single-user applications.

**Key Features:**
- Async I/O with aiosqlite
- Full schema management (17 tables)
- Transaction support
- In-memory database support for testing
- Migration utilities

**Usage:**
```python
from cheap.db.sqlite import SqliteAdapter, SqliteDao

# Create adapter with schema
adapter = await SqliteAdapter.create("data/catalog.db", init_schema=True)
dao = SqliteDao(adapter)

# Save and load catalogs
await dao.save_catalog(catalog)
loaded = await dao.load_catalog(catalog.global_id)
```

### cheap-db-postgres
PostgreSQL persistence for production deployments.

**Key Features:**
- Async I/O with asyncpg
- Connection pooling
- Advanced PostgreSQL features (JSONB, arrays)
- Full transaction support

### cheap-db-mariadb
MariaDB/MySQL persistence with async support.

**Key Features:**
- Async I/O with aiomysql
- Compatible with MySQL 8.0+ and MariaDB 10.5+
- Connection pooling
- UTF-8 support

### cheap-rest
FastAPI-based REST API with multi-database backend support.

**Key Features:**
- Async FastAPI endpoints
- Automatic OpenAPI documentation
- Health checks and monitoring
- Configurable database backends
- Pydantic request/response models

**Usage:**
```bash
# Start the REST API server
uvicorn cheap.rest.main:app --reload

# API available at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

### cheap-rest-client
Python client library for the CHEAP REST API.

**Key Features:**
- Async/sync client support
- Type-safe request/response handling
- Automatic retry and error handling
- Connection pooling

**Usage:**
```python
from cheap.rest.client import AsyncCheapClient
from cheap.core import CatalogSpecies

async with AsyncCheapClient("http://localhost:8000") as client:
    # Create catalog
    catalog = await client.create_catalog(
        species=CatalogSpecies.SOURCE,
        version="1.0.0"
    )

    # Get catalog
    loaded = await client.get_catalog(catalog.catalog_id)
```

### integration-tests
Comprehensive integration test suite covering all modules.

**Test Coverage:**
- Cross-database consistency (15 tests)
- End-to-end REST API (6 tests)
- REST client integration (4 tests)
- Performance benchmarks

## 🏗️ Architecture

### Type System
- **Structural typing** with `typing.Protocol` (no inheritance required)
- **Strict type checking** with basedpyright in strict mode
- **Runtime type validation** with `@runtime_checkable` protocols
- **Full async support** throughout the stack

### Design Patterns
- **Protocol-based interfaces**: Separation of contract from implementation
- **Dataclasses**: Immutable data objects with `frozen=True`
- **Dependency injection**: FastAPI-style dependency injection in REST API
- **Factory pattern**: CheapFactory for creating CHEAP objects
- **DAO pattern**: Database access objects for persistence

### Performance
- **Async I/O**: All database operations are async
- **Connection pooling**: Efficient database connections
- **Slots**: Memory-efficient classes with `__slots__`
- **orjson**: Fast JSON serialization (2-3x faster than stdlib)

## 📖 Documentation

- **[README.md](README.md)**: Project overview and quick start (this file)
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**: Comprehensive API reference for all 8 modules
- **[ASYNC_GUIDE.md](ASYNC_GUIDE.md)**: Complete guide to async/await patterns and best practices
- **[CLAUDE.md](CLAUDE.md)**: Development guide with commands, patterns, and standards
- **[INITIAL_PLAN.md](INITIAL_PLAN.md)**: Complete porting plan and progress tracking
- **Package READMEs**: Each package has detailed README with usage examples

## 🧪 Testing

The project maintains high test coverage across all packages:

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test cross-module interactions
- **E2E tests**: Test full stack from REST API to database
- **Multi-version testing**: Test on Python 3.11, 3.12, 3.13

Test results are available in GitHub Actions CI/CD pipeline.

## 🔧 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Package Manager | uv | Fast dependency resolution |
| Build System | Hatch | Package building and publishing |
| Testing | pytest, pytest-asyncio | Test framework |
| Type Checking | basedpyright | Static type analysis |
| Linting | ruff | Fast linting and formatting |
| Multi-version Testing | nox | Test across Python versions |
| JSON | orjson | High-performance JSON |
| SQLite | aiosqlite | Async SQLite driver |
| PostgreSQL | asyncpg | Async PostgreSQL driver |
| MariaDB | aiomysql | Async MySQL/MariaDB driver |
| REST API | FastAPI | Modern async web framework |
| HTTP Client | httpx | Modern async HTTP client |

## 🤝 Contributing

See [CLAUDE.md](CLAUDE.md) for development workflows and coding standards.

### Pre-commit Checklist

```bash
# 1. Format code (REQUIRED)
nox -s format

# 2. Type check
nox -s typecheck

# 3. Lint
nox -s lint

# 4. Run tests
nox -s tests

# 5. Commit
git add .
git commit -m "Your message"
git push
```

## 📝 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Java Source**: https://github.com/Jelloman/cheap
- **Issue Tracker**: https://github.com/Jelloman/cheap-py/issues
- **CI/CD**: https://github.com/Jelloman/cheap-py/actions

## 🎯 Project Status

**Current Version**: 0.1.0 (Alpha)

**Completed Phases:**
- ✅ Phase 1: Project Setup & Infrastructure
- ✅ Phase 2-3: Core Module (cheap-core)
- ✅ Phase 4: JSON Serialization (cheap-json)
- ✅ Phase 5: SQLite Persistence (cheap-db-sqlite)
- ✅ Phase 6: PostgreSQL Persistence (cheap-db-postgres)
- ✅ Phase 7: MariaDB Persistence (cheap-db-mariadb)
- ✅ Phase 8: REST API (cheap-rest, cheap-rest-client)
- ✅ Phase 9: Integration Tests
- 🔄 Phase 10: Documentation & Refinement (in progress)

All 8 modules are implemented, tested, and fully functional. The project is ready for production use with comprehensive test coverage and quality checks.
