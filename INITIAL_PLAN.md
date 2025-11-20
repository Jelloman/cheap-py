# High-Level Python Port Plan: Cheap → Cheap-Py

## Project Overview
The Cheap Java project is a comprehensive data caching system organized into **8 modules** across three functional categories: core persistence layers, REST API infrastructure, and testing frameworks. It implements the CHEAP model (Catalog, Hierarchy, Entity, Aspect, Property) - a git-like system for structured data.

**This Python port matches the scope of the completed TypeScript port (cheap-ts), covering all 8 modules. All porting should reference the Java implementation, as the TypeScript port is not yet mature or well-tested.**

### Module Structure
**Foundation Modules:**
- `cheap-core` - Core Cheap interfaces and basic implementations (minimal dependencies)
- `cheap-json` - JSON serialization/deserialization using Jackson (Java) → native json/pydantic (Python)
- `cheap-db-sqlite` - SQLite database persistence (development, testing, single-user apps)
- `cheap-db-postgres` - PostgreSQL database persistence (recommended for production)
- `cheap-db-mariadb` - MariaDB/MySQL database persistence

**API & Client Modules:**
- `cheap-rest` - REST API service with multiple database backend support
- `cheap-rest-client` - Python client library for accessing the Cheap REST API

**Testing Infrastructure:**
- `integration-tests` - Cross-database integration tests and performance validation

---

## Phase 1: Project Setup & Infrastructure

### 1.1 Build System Setup
- **Create multi-package Python project** in `/cheap-py` directory
- **Structure:**
  ```
  cheap-py/
  ├── pyproject.toml (monorepo root)
  ├── README.md
  ├── packages/
  │   ├── cheap-core/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/core/
  │   │   └── tests/
  │   ├── cheap-json/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/json/
  │   │   └── tests/
  │   ├── cheap-db-sqlite/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/db/sqlite/
  │   │   └── tests/
  │   ├── cheap-db-postgres/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/db/postgres/
  │   │   └── tests/
  │   ├── cheap-db-mariadb/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/db/mariadb/
  │   │   └── tests/
  │   ├── cheap-rest/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/rest/
  │   │   └── tests/
  │   ├── cheap-rest-client/
  │   │   ├── pyproject.toml
  │   │   ├── src/cheap/rest/client/
  │   │   └── tests/
  │   └── integration-tests/
  │       ├── pyproject.toml
  │       └── tests/
  ```
- **Build tooling:** Poetry or Hatch for workspace/monorepo management
- **Testing:** pytest with pytest-cov for coverage
- **Linting:** ruff (fast linter/formatter) or black + pylint + mypy
- **Type checking:** mypy with strict mode for type safety

### 1.2 Dependency Mapping

**Java → Python equivalents:**
- **Guava** → Python standard library (collections, itertools, functools)
- **Lombok** → dataclasses, attrs, or pydantic
- **JetBrains Annotations** → Type hints (typing module)
- **JUnit Jupiter** → pytest with fixtures
- **Commons Math3** → NumPy or Python's math/decimal modules
- **Jackson** → Built-in json module or pydantic for validation
- **SQLite JDBC** → sqlite3 (built-in) or sqlalchemy
- **PostgreSQL JDBC** → psycopg3 (modern async driver)
- **MariaDB JDBC** → PyMySQL or mysql-connector-python
- **Flyway** → Alembic or yoyo-migrations
- **Spring Boot** → FastAPI or Flask for REST API
- **Spring RestTemplate/WebClient** → httpx or aiohttp for HTTP client
- **Testcontainers** → testcontainers-python for integration tests

---

## Phase 2: Core Module Port (cheap-core)

### 2.1 Type System & Enums
**Priority:** Port fundamental enums first
- `PropertyType` → Python Enum with type validation methods
- `HierarchyType` → Python Enum
- `CatalogSpecies` → Python Enum
- `LocalEntityType` → Python Enum

### 2.2 Model Interfaces & Protocols
**Port Java interfaces to Python Protocols (PEP 544):**
- Core protocols: `Entity`, `Aspect`, `Property`, `PropertyDef`, `AspectDef`
- Catalog protocols: `Catalog`, `CatalogDef`
- Hierarchy protocols: `Hierarchy`, `EntityListHierarchy`, `EntitySetHierarchy`, `EntityDirectoryHierarchy`, `EntityTreeHierarchy`, `AspectMapHierarchy`
- Builder protocols: `AspectBuilder`, `MutableAspectDef`

**Considerations:**
- Java's UUID → Use `uuid` standard library module
- Java's ZonedDateTime → Use `datetime` with `zoneinfo` (Python 3.9+) or `dateutil`
- Java's URI → Use `urllib.parse` or validate as string
- Java's BigInteger/BigDecimal → Use `int` (unlimited precision) and `decimal.Decimal`
- Java interfaces → Use `typing.Protocol` for structural typing or ABC for nominal typing

### 2.3 Basic Implementations
**Port ~30 basic implementation classes:**
- Entity implementations: `EntityImpl`, `EntityLazyIdImpl`, `LocalEntityOneCatalogImpl`, etc.
- Aspect implementations: `AspectBaseImpl`, `AspectPropertyMapImpl`, `AspectObjectMapImpl`
- Hierarchy implementations: All 5 hierarchy types
- Builders: `AspectBuilderBase`, `PropertyDefBuilder`
- Catalog: `CatalogImpl`, `CatalogDefImpl`

**Key decisions:**
- Use `@dataclass` or `attrs` for data classes with automatic __init__, __repr__, etc.
- Consider using `pydantic` for runtime validation
- Use `typing.Final` and immutable types for immutability
- Consider `frozendict` or `immutables` library for immutable collections
- Use `__slots__` for memory optimization on frequently instantiated classes

### 2.4 Reflection-Based Implementations
**Port reflection utilities:**
- Java reflection → Python introspection (`inspect`, `getattr`, `setattr`, `__annotations__`)
- `RecordAspect`, `RecordAspectDef` → Python dataclass with field introspection
- `ImmutablePojoAspect`, `MutablePojoAspect` → Python classes with property descriptors

**Python advantages:**
- Native support for dynamic attribute access
- `__getattr__`, `__setattr__` for custom property access
- `dataclasses.fields()` for field introspection
- Simpler than Java reflection API

### 2.5 Utility Classes
- `CheapFactory` → Factory functions or factory classes
- `CheapFileUtil` → `pathlib.Path` API with async support via `aiofiles`
- `CheapHasher` → `hashlib` standard library module
- Reflection utilities → `inspect` module and custom decorators

---

## Phase 3: JSON Module Port (cheap-json)

### 3.1 Serialization/Deserialization
**Port Jackson serializers to Python:**
- Native `json.dumps()`/`json.loads()` with custom encoder/decoder
- Or use `pydantic` for automatic serialization with validation
- Or use `marshmallow` for schema-based serialization

**Files to port:**
- Serializers: `AspectSerializer`, `AspectDefSerializer`, `CatalogSerializer`, etc.
- Deserializers: `AspectDeserializer`, `CatalogDeserializer`, `HierarchyDeserializer`, etc.

**Python advantages:**
- Custom JSON encoder via `json.JSONEncoder` subclass
- Custom JSON decoder via `object_hook` parameter
- `pydantic` provides automatic serialization for dataclasses

### 3.2 Schema Validation
- Use `pydantic` for runtime validation with type hints
- Or use `marshmallow` for schema definition and validation
- Or use `jsonschema` for JSON Schema validation
- Type guards via `isinstance()` checks

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
- Unit tests for SQLite-specific functionality
- Use in-memory SQLite (`:memory:`) for fast tests
- Test schema creation, migrations, and CRUD operations

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
- Unit tests for PostgreSQL-specific functionality
- Consider testcontainers-python for spinning up PostgreSQL in tests
- Test connection pooling and concurrent access

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
- Unit tests for MariaDB-specific functionality
- Consider testcontainers-python for spinning up MariaDB in tests
- Test character encoding and collation handling

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
- Unit tests for endpoint logic
- Integration tests with test database
- API contract tests
- Load testing for performance baseline

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
- Unit tests with mocked HTTP responses
- Integration tests against real API
- Test error handling and retries
- Test async and sync variants

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
- Ensuring type safety with mypy in complex generic scenarios
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
- **ruff:** Modern, fast linter and formatter (replaces black, isort, flake8)
- **mypy:** Static type checker with strict mode
- **pytest:** Testing framework with rich plugin ecosystem
- **pre-commit:** Git hooks for code quality checks

### Development Workflow
- Use `poetry` or `hatch` for monorepo/workspace management
- Use `tox` or `nox` for testing across Python versions
- Use GitHub Actions or similar for CI/CD
- Use `coverage.py` (via pytest-cov) for test coverage
- Docker Compose for local development with all databases

### Optional Enhancements
- **Pydantic V2:** For runtime validation and serialization (very fast)
- **SQLAlchemy 2.0:** For unified database abstraction layer
- **FastAPI:** For high-performance REST API with automatic docs
- **Type stubs:** For better IDE support and type checking
- **orjson:** For faster JSON serialization than standard library

### CI/CD Pipeline
- Run tests on all supported Python versions (3.10, 3.11, 3.12)
- Test against all database backends in parallel
- Type checking with mypy
- Code coverage reporting
- Performance regression testing
- Docker image building for cheap-rest

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
