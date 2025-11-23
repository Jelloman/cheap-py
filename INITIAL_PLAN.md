# High-Level Python Port Plan: Cheap → Cheap-Py

## Project Overview
The Cheap Java project is a comprehensive data caching system organized into **8 modules** across three functional categories: core persistence layers, REST API infrastructure, and testing frameworks. It implements the CHEAP model (Catalog, Hierarchy, Entity, Aspect, Property) - a git-like system for structured data.

**Source Repository**: The Java implementation is at https://github.com/Jelloman/cheap

**This Python port matches the scope of the completed TypeScript port (cheap-ts), covering all 8 modules. All porting should reference the Java implementation from the repository above, as the TypeScript port is not yet mature or well-tested.**

## Current Status

**Completed:**
- ✅ Phase 1: Project Setup & Infrastructure
- ✅ Phase 2.1: Type System & Enums (PropertyType, HierarchyType, CatalogSpecies)
- ✅ Phase 2.2: Model Interfaces & Protocols (All core protocols defined using structural typing)
- ✅ Phase 2.3: Basic Implementations (All ~14 implementation classes)
- ✅ Phase 2.5: Utility Classes (CheapHasher, CheapFileUtil, CheapFactory)

**In Progress:**
- 🔄 Phase 2.4: Reflection-Based Implementations

**Key Decisions Made:**
- Using **structural typing** (Protocols without explicit inheritance) instead of nominal typing
  - Implementation classes do NOT inherit from Protocols
  - Type safety via duck typing - Impl classes satisfy Protocol structure
  - Eliminates type errors from Protocol/dataclass incompatibility
  - More Pythonic approach
- Using **basedpyright** (strict mode) for type checking instead of standard pyright
- Using **uv** for fast dependency management and workspace coordination

### Module Structure
**Foundation Modules:**
- `cheap-core` - Core Cheap interfaces and basic implementations (minimal dependencies)
- `cheap-json` - JSON serialization/deserialization using Jackson (Java) → orjson (Python)
- `cheap-db-sqlite` - SQLite database persistence (development, testing, single-user apps)
- `cheap-db-postgres` - PostgreSQL database persistence (recommended for production)
- `cheap-db-mariadb` - MariaDB/MySQL database persistence

**API & Client Modules:**
- `cheap-rest` - REST API service with multiple database backend support
- `cheap-rest-client` - Python client library for accessing the Cheap REST API

**Testing Infrastructure:**
- `integration-tests` - Cross-database integration tests and performance validation

### Implementation Standards
- **Type hints:** Use Python type hints throughout the codebase for all functions, methods, and variables
- **Static analysis:** Use basedpyright (pyright fork) for static type checking in strict mode
- **JSON serialization:** Use orjson for high-performance JSON with native UUID and datetime support
- **Build system:** Use uv for dependency management and Hatch for monorepo management and packaging
- **Multi-version testing:** Use Nox for testing across multiple Python versions (3.11, 3.12, 3.13, 3.14)

---

## Phase 1: Project Setup & Infrastructure

### 1.1 Build System Setup
- **Create multi-package Python project** in `/cheap-py` directory using Hatch
- **Structure:**
  ```
  cheap-py/
  ├── pyproject.toml (monorepo root - uv workspace)
  ├── noxfile.py (multi-version testing configuration)
  ├── pyrightconfig.json (basedpyright configuration)
  ├── .github/
  │   └── workflows/
  │       ├── build-cheap-python.yml
  │       ├── integration-tests.yml
  │       └── docker-integration-tests.yml
  ├── README.md
  ├── packages/
  │   ├── cheap-core/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/core/
  │   │   │   ├── __init__.py
  │   │   │   └── py.typed
  │   │   └── tests/
  │   ├── cheap-json/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/json/
  │   │   │   ├── __init__.py
  │   │   │   └── py.typed
  │   │   └── tests/
  │   ├── cheap-db-sqlite/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/db/sqlite/
  │   │   │   ├── __init__.py
  │   │   │   └── py.typed
  │   │   └── tests/
  │   ├── cheap-db-postgres/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/db/postgres/
  │   │   │   ├── __init__.py
  │   │   │   └── py.typed
  │   │   └── tests/
  │   ├── cheap-db-mariadb/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/db/mariadb/
  │   │   │   ├── __init__.py
  │   │   │   └── py.typed
  │   │   └── tests/
  │   ├── cheap-rest/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/rest/
  │   │   │   ├── __init__.py
  │   │   │   └── py.typed
  │   │   └── tests/
  │   ├── cheap-rest-client/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/rest/client/
  │   │   │   ├── __init__.py
  │   │   │   └── py.typed
  │   │   └── tests/
  │   └── integration-tests/
  │       ├── pyproject.toml
  │       └── tests/
  ```

- **Build tooling:**
  - **Hatch** - Modern Python project manager with excellent monorepo/workspace support
  - Supports building, versioning, and publishing multiple packages
  - Built-in environment management
  - Configuration via `pyproject.toml`

- **Multi-version testing:**
  - **Nox** - Automated testing across multiple Python versions (3.10, 3.11, 3.12, 3.13)
  - Define test sessions for unit tests, integration tests, type checking, linting
  - Simpler than tox with Python-based configuration

- **Testing:**
  - pytest with pytest-cov for coverage
  - pytest-asyncio for async test support
  - pytest-xdist for parallel test execution

- **Linting:** ruff (fast linter and formatter - replaces black, isort, flake8, pylint)

- **Type checking:**
  - **Pyright** - Microsoft's static type checker (faster than mypy, better IDE integration)
  - Run in strict mode for maximum type safety
  - Include type checking as part of unit test runs (via pytest plugin or nox session)
  - Download and install .pyi stub files for all third-party libraries where available
  - Use `py.typed` marker in each package to indicate type hint support (PEP 561)

### 1.2 Dependency Mapping

**Java → Python equivalents:**
- **Guava** → Python standard library (collections, itertools, functools)
- **Lombok** → dataclasses with type hints (prefer built-in dataclasses)
- **JetBrains Annotations (@NotNull/@Nullable)** → Type hints (typing module with strict Optional typing)
- **JUnit Jupiter** → pytest with fixtures and type-annotated test functions
- **Commons Math3** → Python's math/decimal modules (decimal.Decimal for precision)
- **Jackson** → **orjson** (high-performance JSON with native UUID and datetime serialization)
- **SQLite JDBC** → sqlite3 (built-in) or aiosqlite (async)
- **PostgreSQL JDBC** → psycopg3 (modern async driver with full type hint support)
- **MariaDB JDBC** → PyMySQL or mysql-connector-python
- **Flyway** → Alembic or yoyo-migrations for database migrations
- **Spring Boot** → FastAPI (recommended - excellent type hint support and auto-documentation)
- **Spring RestTemplate/WebClient** → httpx (modern, type-safe HTTP client with async support)
- **Testcontainers** → testcontainers-python for integration tests

**Key Python-specific libraries:**
- **orjson** - Ultra-fast JSON library with native support for:
  - UUID serialization/deserialization
  - datetime/date/time serialization
  - numpy types (if needed)
  - 2-5x faster than standard json library
- **Pyright** - Static type checker with comprehensive type analysis
- **types-*** packages - Type stubs for third-party libraries (e.g., types-requests, types-redis)

### 1.3 GitHub Actions Workflows

Set up three GitHub Actions workflows matching the Java repository structure:

#### 1.3.1 Build Workflow (`build-cheap-python.yml`)
**Triggers:** Push events affecting module paths
- `packages/cheap-core/**`
- `packages/cheap-json/**`
- `packages/cheap-db-sqlite/**`
- `packages/cheap-db-postgres/**`
- `packages/cheap-db-mariadb/**`
- `packages/cheap-rest/**`
- `packages/cheap-rest-client/**`
- `packages/integration-tests/**`
- `pyproject.toml`
- `noxfile.py`
- `.github/workflows/build-cheap-python.yml`

**Jobs:**
1. **Checkout code** (actions/checkout@v4)
2. **Setup Python matrix** - Test on Python 3.10, 3.11, 3.12, 3.13 using actions/setup-python@v5
3. **Install Hatch** - Install build system
4. **Install dependencies** - Use Hatch to install all workspace packages
5. **Run Pyright** - Static type checking across all modules
6. **Run tests** - Execute `nox -s tests` for all modules
7. **Run linting** - Execute `nox -s lint` with ruff
8. **Generate coverage report** - Combine coverage from all modules
9. **Upload test results** - Archive test reports and coverage (actions/upload-artifact@v4, runs on failure too)
10. **Upload packages** - Archive built wheel files for all packages

#### 1.3.2 Integration Tests Workflow (`integration-tests.yml`)
**Triggers:** Manual dispatch (workflow_dispatch)

**Jobs:**
1. **Checkout code** (actions/checkout@v4)
2. **Setup Python** - Python 3.12 (primary version)
3. **Install Hatch**
4. **Install dependencies**
5. **Run integration tests** - Execute `nox -s integration_tests`
   - Tests with SQLite, PostgreSQL, and MariaDB
   - Uses in-process databases or testcontainers
6. **Upload test results** - Archive integration test reports (if: always())

**Note:** Implement this workflow once integration-tests module is ready

#### 1.3.3 Docker Integration Tests Workflow (`docker-integration-tests.yml`)
**Triggers:** Manual dispatch (workflow_dispatch)

**Jobs:**
1. **Checkout code** (actions/checkout@v4)
2. **Setup Python** - Python 3.12
3. **Install Hatch**
4. **Setup Docker** - Ensure Docker is available
5. **Run dockerized integration tests** - Execute `nox -s docker_integration_tests`
   - Spin up PostgreSQL and MariaDB containers
   - Run full integration test suite against real databases
   - Test REST API with all database backends
6. **Upload test results** - Archive test reports and logs (if: always())

**Note:** Implement this workflow once Docker-based tests are implemented

#### Workflow Implementation Priority
1. **Start with build workflow** - Implement immediately for CI/CD
2. **Add integration tests workflow** - Once Phase 9 (integration-tests) is started
3. **Add Docker integration tests** - Once containerized tests are implemented

---

## Phase 2: Core Module Port (cheap-core)

### 2.1 Type System & Enums ✅ COMPLETED
**Priority:** Port fundamental enums first with full type annotations
- `PropertyType` → Python Enum with type validation methods (fully type-hinted)
- `HierarchyType` → Python Enum (fully type-hinted)
- `CatalogSpecies` → Python Enum (fully type-hinted)
- `LocalEntityType` → Python Enum (fully type-hinted)

**Type hint requirements:**
- All enum methods must have complete type signatures
- Use `typing.Literal` for enum value types where appropriate
- Ensure Pyright can infer all types correctly

### 2.2 Model Interfaces & Protocols ✅ COMPLETED
**Port Java interfaces to Python Protocols (PEP 544) with full type annotations:**
- Core protocols: `Entity`, `Aspect`, `Property`, `PropertyDef`, `AspectDef`
- Catalog protocols: `Catalog`, `CatalogDef`
- Hierarchy protocols: `Hierarchy`, `EntityListHierarchy`, `EntitySetHierarchy`, `EntityDirectoryHierarchy`, `EntityTreeHierarchy`, `AspectMapHierarchy`
- Builder protocols: `AspectBuilder`, `MutableAspectDef`

**Type annotation requirements:**
- Use `typing.Protocol` for all interface definitions
- Add complete type signatures for all protocol methods
- Use generic protocols with `typing.TypeVar` where needed
- Ensure all return types and parameters are fully annotated
- Use `typing.Self` (Python 3.11+) for builder pattern return types

**Considerations:**
- Java's UUID → Use `uuid.UUID` with full type hints
- Java's ZonedDateTime → Use `datetime.datetime` with `zoneinfo` (Python 3.9+) or `dateutil.tz`
- Java's URI → Use `str` with runtime validation or custom URI type
- Java's BigInteger/BigDecimal → Use `int` (unlimited precision) and `decimal.Decimal` with type hints
- Java interfaces → Use `typing.Protocol` for structural typing **WITHOUT explicit inheritance**
  - **IMPORTANT:** Implementation classes do NOT inherit from Protocols
  - Use `@runtime_checkable` decorator on Protocols for isinstance() checks
  - Protocols define structure; Impl classes satisfy structure via duck typing
  - This avoids type errors from Protocol @property vs dataclass field incompatibility
- All protocol methods must be fully type-annotated for basedpyright compatibility

### 2.3 Basic Implementations ✅ COMPLETED
**Implemented 14 core classes with complete type annotations:**
- ✅ Property implementations: `PropertyDefImpl`, `PropertyImpl`
- ✅ Aspect implementations: `AspectDefImpl`, `AspectImpl`
- ✅ Entity implementation: `EntityImpl`
- ✅ Hierarchy implementations: All 5 types (`EntityListHierarchyImpl`, `EntitySetHierarchyImpl`, `EntityDirectoryHierarchyImpl`, `EntityTreeHierarchyImpl`, `AspectMapHierarchyImpl`)
- ✅ Tree node: `EntityTreeNodeImpl`
- ✅ Catalog implementations: `HierarchyDefImpl`, `CatalogDefImpl`, `CatalogImpl`
- ✅ All classes use Protocol types in collections (e.g., `dict[str, PropertyDef]` not `dict[str, PropertyDefImpl]`)
- ✅ 23 tests passing, zero type errors

**Key decisions:**
- Use `@dataclass` (preferred) for data classes with automatic __init__, __repr__, etc.
  - Always include complete type hints for all fields
  - Use `dataclass(frozen=True)` for immutable classes
  - Use `dataclass(slots=True)` (Python 3.10+) for memory efficiency
- **Comprehensive type hints required:**
  - All method parameters and return types
  - All class attributes and instance variables
  - Use `typing.ClassVar` for class variables
  - Use `typing.Final` for constants and immutable attributes
- Consider `frozendict` or `immutables` library for immutable collections
- Ensure all code passes Pyright in strict mode

### 2.4 Reflection-Based Implementations 🔄 IN PROGRESS
**Port reflection utilities:**
- Java reflection → Python introspection (`inspect`, `getattr`, `setattr`, `__annotations__`)
- `RecordAspect`, `RecordAspectDef` → Python dataclass with field introspection
- `ImmutablePojoAspect`, `MutablePojoAspect` → Python classes with property descriptors

**Python advantages:**
- Native support for dynamic attribute access
- `__getattr__`, `__setattr__` for custom property access
- `dataclasses.fields()` for field introspection
- Simpler than Java reflection API

### 2.5 Utility Classes 🔄 IN PROGRESS
- `CheapFactory` → Factory functions or factory classes
- `CheapFileUtil` → `pathlib.Path` API with async support via `aiofiles`
- `CheapHasher` → `hashlib` standard library module
- Reflection utilities → `inspect` module and custom decorators

---

## Phase 3: JSON Module Port (cheap-json)

### 3.1 Serialization/Deserialization with orjson
**Use orjson for high-performance JSON serialization:**

**Why orjson:**
- **Native UUID support:** Automatically serializes/deserializes `uuid.UUID` objects
- **Native datetime support:** Handles `datetime`, `date`, and `time` objects natively
- **Performance:** 2-5x faster than standard json library
- **Type safety:** Works seamlessly with type hints
- **Standards compliant:** RFC 8259 compliant JSON output

**Files to port:**
- Serializers: `AspectSerializer`, `AspectDefSerializer`, `CatalogSerializer`, etc.
- Deserializers: `AspectDeserializer`, `CatalogDeserializer`, `HierarchyDeserializer`, etc.

**Implementation approach:**
```python
import orjson
from typing import Any
from uuid import UUID
from datetime import datetime

# Serialization (orjson handles UUID and datetime natively)
def serialize_aspect(aspect: Aspect) -> bytes:
    return orjson.dumps(
        aspect,
        option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY
    )

# Deserialization with type hints
def deserialize_aspect(data: bytes) -> Aspect:
    parsed: dict[str, Any] = orjson.loads(data)
    # Convert to Aspect object with proper type checking
    return Aspect(**parsed)
```

**Key features to leverage:**
- `orjson.OPT_NAIVE_UTC` - Serialize naive datetimes as UTC
- `orjson.OPT_SERIALIZE_UUID` - Already default, UUIDs serialized as strings
- `orjson.OPT_SORT_KEYS` - Deterministic output for testing
- `default` parameter - Custom serialization for unsupported types

**Type hint requirements:**
- All serialization functions must be fully type-hinted
- Use `bytes` for orjson output (returns bytes, not str)
- Define TypedDict or dataclass types for JSON schema validation
- Ensure Pyright can verify all type conversions

### 3.2 Schema Validation
- Leverage type hints with runtime validation where needed
- Use Pyright to catch type errors at development time
- Consider `pydantic` for complex runtime validation scenarios
- Use `typing.TypedDict` for JSON object structure definitions
- Type guards via `isinstance()` checks for runtime safety
- Validate using type-annotated dataclasses/protocols

---

## Phase 4: SQLite Database Module Port (cheap-db-sqlite)

### 4.1 Database Abstraction Layer
**Port JDBC-based code to Python database drivers:**
- `JdbcCatalogBase` → Abstract base class using async/await or sync API
- Consider SQLAlchemy Core (not ORM) for database abstraction

### 4.2 SQLite Implementation
- **SQLite:** `SqliteCatalog`, `SqliteDao`, `SqliteCheapSchema`
  - Use `sqlite3` (built-in) or `aiosqlite` (async)
  - Consider `sqlalchemy` for unified API across database modules
  - Ideal for development, testing, and single-user applications

### 4.3 Migration Strategy
- Port Flyway SQL migrations to Alembic or yoyo-migrations
- Ensure schema compatibility between Java and Python versions
- SQLAlchemy Core provides type-safe query building without ORM overhead
- Consider async database drivers for better I/O performance

### 4.4 Testing
- Unit tests for SQLite-specific functionality (fully type-hinted)
- Use in-memory SQLite (`:memory:`) for fast tests
- Test schema creation, migrations, and CRUD operations
- **Include Pyright static analysis:**
  - Run `pyright` as part of test suite
  - Use `pytest-pyright` plugin or nox session
  - Ensure zero type errors before tests pass

---

## Phase 5: PostgreSQL Database Module Port (cheap-db-postgres)

### 5.1 PostgreSQL Implementation
- **PostgreSQL:** `PostgresCatalog`, `PostgresDao`, `PostgresCheapSchema`
  - Use `psycopg3` (modern, fast, async support)
  - Or `asyncpg` for pure async performance
  - Recommended for production deployments

### 5.2 Connection Pooling
- Use connection pooling for production deployments
- `psycopg3` has built-in connection pooling
- Consider `sqlalchemy` engine pooling for unified interface

### 5.3 PostgreSQL-Specific Features
- Leverage PostgreSQL-specific types (JSONB, Arrays, etc.)
- Use proper transaction isolation levels
- Implement connection retry logic

### 5.4 Testing
- Unit tests for PostgreSQL-specific functionality (fully type-hinted)
- Consider testcontainers-python for spinning up PostgreSQL in tests
- Test connection pooling and concurrent access
- **Include Pyright static analysis:** Run as part of test suite

---

## Phase 6: MariaDB Database Module Port (cheap-db-mariadb)

### 6.1 MariaDB Implementation
- **MariaDB/MySQL:** `MariaDbCatalog`, `MariaDbDao`, `MariaDbCheapSchema`
  - Use `PyMySQL` (pure Python) or `mysql-connector-python` (official)
  - Or `aiomysql` for async support
  - Support for MySQL/MariaDB-specific features

### 6.2 MySQL/MariaDB Compatibility
- Handle differences between MySQL and MariaDB
- Test with both database engines if possible
- Consider version-specific features

### 6.3 Testing
- Unit tests for MariaDB-specific functionality (fully type-hinted)
- Consider testcontainers-python for spinning up MariaDB in tests
- Test character encoding and collation handling
- **Include Pyright static analysis:** Run as part of test suite

---

## Phase 7: REST API Module Port (cheap-rest)

### 7.1 Framework Selection
**Choose Python web framework:**
- **FastAPI** (Recommended) - Modern, async, automatic OpenAPI docs, type hints
- **Flask** - Lightweight, mature, large ecosystem
- **Django REST Framework** - Full-featured but heavier

### 7.2 REST API Implementation
**Port Spring Boot REST controllers to Python:**
- Entity CRUD endpoints
- Catalog management endpoints
- Hierarchy query endpoints
- Aspect manipulation endpoints
- Database backend configuration (SQLite/PostgreSQL/MariaDB)

**FastAPI advantages:**
- Automatic OpenAPI/Swagger documentation
- Request/response validation via Pydantic
- Native async/await support
- Dependency injection system
- Built-in security utilities

### 7.3 Database Backend Support
- Support multiple database backends via configuration
- Connection pooling for production
- Health check endpoints
- Graceful startup/shutdown

### 7.4 API Documentation
- Generate OpenAPI/Swagger documentation (automatic with FastAPI)
- Document authentication/authorization requirements
- Provide example requests/responses
- Version the API appropriately

### 7.5 Testing
- Unit tests for endpoint logic (fully type-hinted)
- Integration tests with test database
- API contract tests
- Load testing for performance baseline
- **Include Pyright static analysis:** Verify all endpoint type signatures

---

## Phase 8: REST Client Module Port (cheap-rest-client)

### 8.1 HTTP Client Implementation
**Port Spring RestTemplate/WebClient to Python:**
- Use `httpx` (modern, async support) or `aiohttp`
- Provide both sync and async API variants
- Type-safe request/response handling

### 8.2 Client API Design
**Port Java client methods to Python:**
- Entity operations: create, read, update, delete
- Catalog operations: list, get, create
- Hierarchy operations: query, traverse
- Aspect operations: add, update, remove

**Python advantages:**
- Context managers for connection management
- Async/await for concurrent requests
- Type hints for IDE autocompletion
- Pydantic models for response validation

### 8.3 Error Handling
- Map HTTP status codes to Python exceptions
- Retry logic with exponential backoff
- Timeout configuration
- Connection pooling

### 8.4 Authentication & Configuration
- Support various auth mechanisms (API keys, OAuth, etc.)
- Configuration via environment variables or config files
- Session management
- Request logging and debugging

### 8.5 Testing
- Unit tests with mocked HTTP responses (fully type-hinted)
- Integration tests against real API
- Test error handling and retries
- Test async and sync variants
- **Include Pyright static analysis:** Verify client method type signatures

---

## Phase 9: Integration Tests Module Port (integration-tests)

### 9.1 Cross-Database Testing
**Validate consistency across all database backends:**
- Test same operations on SQLite, PostgreSQL, and MariaDB
- Verify identical behavior across databases
- Ensure schema compatibility
- Test migrations on all backends

### 9.2 End-to-End Testing
**Full system integration tests:**
- REST API → Database → Response cycle
- REST Client → REST API → Database integration
- Complex multi-entity scenarios
- Transaction handling and rollback

### 9.3 Performance Testing
**Establish performance baselines:**
- Bulk insert/update/delete operations
- Query performance across different hierarchy types
- Concurrent access patterns
- Memory usage profiling

### 9.4 Test Infrastructure
**Setup test environment:**
- Use `testcontainers-python` for database containers
- Docker Compose for full stack testing
- Fixtures for common test data
- Parallel test execution with pytest-xdist

### 9.5 Testing Tools
- **pytest** for test framework
- **testcontainers-python** for spinning up databases
- **pytest-asyncio** for async test support
- **pytest-xdist** for parallel execution
- **locust** or **pytest-benchmark** for performance testing

---

## Phase 10: Documentation & Refinement

### 10.1 Documentation
- Port JavaDoc comments to Python docstrings (Google or NumPy style)
- Generate documentation with Sphinx or MkDocs
- Create Python-specific README files for each module
- Document API differences from Java version
- Add type stubs (.pyi files) if needed for better IDE support
- Create comprehensive API documentation
- Write migration guide from Java to Python

### 10.2 Build & Distribution
- Set up PyPI publishing workflow for each package
- Use `poetry build` or `hatch build` for package building
- Include py.typed file for PEP 561 type hint distribution
- Support Python 3.10+ (or 3.9+ if broader compatibility needed)
- Semantic versioning aligned with Java version

### 10.3 Performance Optimization
- Profile hot paths with `cProfile` or `py-spy`
- Consider Cython for performance-critical sections
- Use `__slots__` for memory-efficient classes
- Consider `orjson` for faster JSON serialization
- Use `multiprocessing` or `asyncio` for concurrency
- Benchmark against Java implementation

### 10.4 Async Support
- Provide async variants of database operations (recommended)
- Use `asyncio` for I/O-bound operations
- Async REST API endpoints
- Async REST client methods
- Document async usage patterns

---

## Key Technical Decisions

### Type System Mapping
| Java Pattern | Python Approach |
|--------------|-----------------|
| Interface + Implementation | Protocol/ABC + Class |
| Generics `<T extends Foo>` | `TypeVar` with bounds: `T = TypeVar('T', bound=Foo)` |
| `@NotNull` / `@Nullable` | Non-optional / `Optional[T]` or `T \| None` |
| Lombok getters/setters | `@property` decorator or dataclass |
| Reflection | `inspect` module, `__annotations__`, `getattr`/`setattr` |
| Enums | `enum.Enum` or `enum.StrEnum` |
| Collections | `list`, `dict`, `set`, or `typing` generics |
| Spring DI | FastAPI dependencies or manual dependency injection |

### Immutability Strategy
- Use `@dataclass(frozen=True)` for immutable dataclasses
- Use `tuple` instead of `list` for immutable sequences
- Use `frozenset` instead of `set` for immutable sets
- Consider `frozendict` library for immutable dictionaries
- Use `typing.Final` for constants

### Async/Await Patterns
- Python has native async/await support
- Database drivers have excellent async support (psycopg3, aiosqlite, asyncpg)
- Provide async-first API for better I/O performance
- Use `asyncio.gather()` for concurrent operations
- FastAPI has native async support

### Module System
- Use standard Python package structure
- Separate package for each module (monorepo with multiple packages)
- Absolute imports from package root
- Proper `__init__.py` with `__all__` for public API
- Consider namespace packages for extensibility

### Python Advantages Over Java
- **Dynamic typing with gradual typing:** More flexible, type hints optional
- **First-class functions:** Easier callbacks and functional patterns
- **Simpler syntax:** Less boilerplate than Java
- **Better REPL:** Interactive development and debugging
- **Native async support:** Built into the language
- **Unlimited precision integers:** No separate BigInteger class needed
- **Multiple inheritance:** More flexible class hierarchies
- **Duck typing with Protocols:** Structural subtyping without explicit interfaces

---

## Module Dependency Graph

```
cheap-core (foundation)
    ↓
cheap-json (depends on cheap-core)
    ↓
┌────────────────────┬────────────────────┐
│                    │                    │
cheap-db-sqlite  cheap-db-postgres  cheap-db-mariadb
│                    │                    │
└────────────────────┴────────────────────┘
                     ↓
              cheap-rest (depends on cheap-core, cheap-json, all cheap-db-*)
                     ↓
           cheap-rest-client (depends on cheap-core, cheap-json)
                     ↓
         integration-tests (depends on all modules)
```

---

## Estimated Complexity

**Module Breakdown:**
1. **cheap-core:** ~5,000-7,000 LOC (Python is ~30-40% more concise than Java)
2. **cheap-json:** ~1,000-1,500 LOC
3. **cheap-db-sqlite:** ~800-1,200 LOC
4. **cheap-db-postgres:** ~800-1,200 LOC
5. **cheap-db-mariadb:** ~800-1,200 LOC
6. **cheap-rest:** ~1,500-2,500 LOC
7. **cheap-rest-client:** ~1,000-1,500 LOC
8. **integration-tests:** ~1,500-2,500 LOC

**Total:** ~12,400-18,600 LOC

**Time Estimate:** 20-30 weeks for complete implementation across all 8 modules

**Module Priority:**
1. **cheap-core** (highest) - Foundation for everything else
2. **cheap-json** - Needed for testing/debugging
3. **cheap-db-sqlite** - Easiest database, good for development
4. **cheap-db-postgres** - Production database
5. **cheap-db-mariadb** - Additional database option
6. **cheap-rest** - API layer
7. **cheap-rest-client** - Client library
8. **integration-tests** - Final validation

**Risk Areas:**
- Ensuring type safety with Pyright in complex generic scenarios
- Database async patterns and connection management
- Performance compared to Java (may need optimization)
- Memory usage with large datasets (Python has higher overhead)
- REST API performance under load
- Cross-database consistency

**Python-Specific Considerations:**
- GIL (Global Interpreter Lock) may limit CPU-bound parallelism
- Consider `multiprocessing` for CPU-bound operations
- Memory usage is higher than Java; monitor carefully
- Dynamic typing requires discipline with type hints
- Async I/O performance is excellent with modern drivers

---

## Additional Recommendations

### Code Quality Tools
- **Pyright:** Static type checker with strict mode (primary type checker)
- **ruff:** Modern, fast linter and formatter (replaces black, isort, flake8)
- **pytest:** Testing framework with rich plugin ecosystem
- **pytest-pyright:** Integration of Pyright with pytest
- **pre-commit:** Git hooks for code quality checks (include Pyright and ruff)

### Development Workflow
- **Use Hatch for monorepo/workspace management:**
  - Modern Python project manager
  - Excellent workspace support for multiple packages
  - Built-in environment management
  - Simplified build and publish workflows
- **Use Nox for testing across Python versions:**
  - Test against Python 3.10, 3.11, 3.12, 3.13
  - Define sessions for: tests, lint, typecheck, integration-tests
  - Python-based configuration (more flexible than tox)
  - Easy CI/CD integration
- Use GitHub Actions for CI/CD (3 workflows as defined in Phase 1.3)
- Use `coverage.py` (via pytest-cov) for test coverage
- Docker Compose for local development with all databases
- Download .pyi stub files for all third-party dependencies:
  - Install types-* packages (e.g., types-requests, types-redis)
  - Check PyPI for stub packages for each dependency
  - Configure Pyright to use stub paths

#### Pre-Commit Workflow (CRITICAL)
**ALWAYS run formatting before committing** to ensure GitHub Actions checks pass:

```bash
# 1. Format code with ruff (REQUIRED before every commit)
nox -s format

# 2. Run type checking
nox -s typecheck

# 3. Run tests
nox -s tests

# 4. Stage and commit
git add <files>
git commit -m "Your commit message"

# 5. Push
git push -u origin <branch-name>
```

**Pre-Commit Checklist**:
- ✓ `nox -s format` - Auto-format all code (REQUIRED)
- ✓ `nox -s typecheck` - Verify no type errors
- ✓ `nox -s tests` - Ensure all tests pass
- ✓ All three must pass before pushing

**Why**: GitHub Actions will reject commits with formatting/linting errors. Running `nox -s format` before committing prevents CI failures.

### Optional Enhancements
- **Pydantic V2:** For runtime validation and serialization (very fast) - useful for REST API
- **SQLAlchemy 2.0:** For unified database abstraction layer across all database modules

### Required Technologies (Summary)
The following are **required** (not optional) for this project:
- **Hatch:** Monorepo/workspace management and packaging
- **Nox:** Multi-version testing automation
- **Pyright:** Static type analysis (strict mode)
- **orjson:** High-performance JSON with native UUID/datetime support
- **Type hints:** Complete type annotations throughout the codebase
- **FastAPI:** For REST API implementation (recommended framework)

### CI/CD Pipeline
- Run tests on all supported Python versions (3.10, 3.11, 3.12, 3.13) via Nox
- Test against all database backends in parallel
- **Type checking with Pyright** (strict mode, zero errors required)
- Code coverage reporting (target: 80%+ coverage)
- Linting with ruff (formatting and code quality)
- Performance regression testing
- Docker image building for cheap-rest
- See Phase 1.3 for complete GitHub Actions workflow definitions

### Nox Configuration Example
Create a `noxfile.py` in the repository root:

```python
import nox

# Supported Python versions
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run unit tests for all packages."""
    session.install("hatch")
    session.run("hatch", "run", "test:pytest", "-v", "--cov")

@nox.session(python="3.12")
def typecheck(session):
    """Run Pyright type checking."""
    session.install("hatch", "pyright")
    session.run("pyright", "packages/")

@nox.session(python="3.12")
def lint(session):
    """Run ruff linting and formatting."""
    session.install("ruff")
    session.run("ruff", "check", "packages/")
    session.run("ruff", "format", "--check", "packages/")

@nox.session(python="3.12")
def integration_tests(session):
    """Run integration tests."""
    session.install("hatch")
    session.run("hatch", "run", "test:pytest", "packages/integration-tests/")

@nox.session(python="3.12")
def docker_integration_tests(session):
    """Run dockerized integration tests."""
    session.install("hatch", "testcontainers")
    session.run("hatch", "run", "test:pytest", "packages/integration-tests/", "-m", "docker")
```

---

## Alignment with TypeScript Port

This plan matches the scope of the completed TypeScript port (cheap-ts), which covers all 8 modules:
1. ✅ cheap-core
2. ✅ cheap-json
3. ✅ cheap-db-sqlite
4. ✅ cheap-db-postgres
5. ✅ cheap-db-mariadb
6. ✅ cheap-rest
7. ✅ cheap-rest-client
8. ✅ integration-tests

**Important:** All porting work should reference the **Java implementation only**, as the TypeScript port is not yet mature or well-tested. The TypeScript port serves as a reference for scope and structure, but not for implementation details.

---

This plan provides a comprehensive, structured approach to porting all 8 modules of the Cheap Java project to Python while leveraging Python's strengths (async support, dynamic typing, simpler syntax) and maintaining architectural integrity. The modular structure allows for incremental development and testing, with clear dependencies between phases.
