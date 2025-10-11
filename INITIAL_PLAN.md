# High-Level Python Port Plan: Cheap → Cheap-Py

## Project Overview
The Cheap Java project is a data caching system with ~137 Java files organized into 3 modules (cheap-core, cheap-db, cheap-json). It implements the CHEAP model (Catalog, Hierarchy, Entity, Aspect, Property) - a git-like system for structured data.

---

## Phase 1: Project Setup & Infrastructure

### 1.1 Build System Setup
- **Create multi-package Python project** in `/cheap-py` directory
- **Structure:**
  ```
  cheap-py/
  ├── pyproject.toml (project metadata)
  ├── README.md
  ├── src/
  │   └── cheap/
  │       ├── __init__.py
  │       ├── core/          # cheap-core equivalent
  │       ├── db/            # cheap-db equivalent
  │       └── json/          # cheap-json equivalent
  ├── tests/
  │   ├── core/
  │   ├── db/
  │   └── json/
  ```
- **Build tooling:** Poetry or Hatch for dependency management and building
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

---

## Phase 2: Core Module Port (cheap.core)

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

## Phase 3: Database Module Port (cheap.db)

### 3.1 Database Abstraction Layer
**Port JDBC-based code to Python database drivers:**
- `JdbcCatalogBase` → Abstract base class using async/await or sync API
- Database-specific schemas: SQLite, PostgreSQL, MariaDB
- Consider SQLAlchemy Core (not ORM) for database abstraction

### 3.2 Database Implementations
- **SQLite:** `SqliteCatalog`, `SqliteDao`, `SqliteCheapSchema`
  - Use `sqlite3` (built-in) or `aiosqlite` (async)
  - Consider `sqlalchemy` for unified API
- **PostgreSQL:** `PostgresCatalog`, `PostgresDao`, `PostgresCheapSchema`
  - Use `psycopg3` (modern, fast, async support)
  - Or `asyncpg` for pure async performance
- **MariaDB/MySQL:** `MariaDbCatalog`, `MariaDbDao`, `MariaDbCheapSchema`
  - Use `PyMySQL` (pure Python) or `mysql-connector-python` (official)
  - Or `aiomysql` for async support

### 3.3 Migration Strategy
- Port Flyway SQL migrations to Alembic or yoyo-migrations
- Ensure schema compatibility between Java and Python versions
- SQLAlchemy Core provides type-safe query building without ORM overhead
- Consider async database drivers for better I/O performance

### 3.4 Connection Pooling
- Use connection pooling for production deployments
- `psycopg3` has built-in connection pooling
- Consider `sqlalchemy` engine pooling for unified interface

---

## Phase 4: JSON Module Port (cheap.json)

### 4.1 Serialization/Deserialization
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

### 4.2 Schema Validation
- Use `pydantic` for runtime validation with type hints
- Or use `marshmallow` for schema definition and validation
- Or use `jsonschema` for JSON Schema validation
- Type guards via `isinstance()` checks

---

## Phase 5: Testing Strategy

### 5.1 Unit Tests
- Port existing JUnit tests to pytest
- Use `pytest.fixture` for test setup/teardown (replaces JUnit @BeforeEach/@AfterEach)
- Use `pytest.mark.parametrize` for data-driven tests
- Maintain test coverage parity with Java version (use pytest-cov)
- Use immutable collections in tests where possible
- Use fixed UUIDs in tests for deterministic behavior

### 5.2 Integration Tests
- Test database persistence layer with real databases
- Use `pytest-docker` or `testcontainers-python` for database containers
- Or use in-memory SQLite for lightweight tests
- Port Flyway/embedded database tests to Python equivalents

### 5.3 Type Checking Tests
- Run `mypy` as part of CI/CD pipeline
- Ensure all public APIs are fully type-annotated
- Use `typing.Protocol` for structural type checking

---

## Phase 6: Documentation & Refinement

### 6.1 Documentation
- Port JavaDoc comments to Python docstrings (Google or NumPy style)
- Generate documentation with Sphinx or MkDocs
- Create Python-specific README files for each module
- Document API differences from Java version
- Add type stubs (.pyi files) if needed for better IDE support

### 6.2 Build & Distribution
- Set up PyPI publishing workflow
- Use `poetry build` or `hatch build` for package building
- Include py.typed file for PEP 561 type hint distribution
- Support Python 3.10+ (or 3.9+ if broader compatibility needed)

### 6.3 Performance Optimization
- Profile hot paths with `cProfile` or `py-spy`
- Consider Cython for performance-critical sections
- Use `__slots__` for memory-efficient classes
- Consider `orjson` for faster JSON serialization
- Use `multiprocessing` or `asyncio` for concurrency

### 6.4 Async Support (Optional but Recommended)
- Consider async variants of database operations
- Use `asyncio` for I/O-bound operations
- Provide both sync and async APIs (or async-only for simplicity)

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

### Immutability Strategy
- Use `@dataclass(frozen=True)` for immutable dataclasses
- Use `tuple` instead of `list` for immutable sequences
- Use `frozenset` instead of `set` for immutable sets
- Consider `frozendict` library for immutable dictionaries
- Use `typing.Final` for constants

### Async/Await Patterns
- Python has native async/await support
- Database drivers have excellent async support (psycopg3, aiosqlite, asyncpg)
- Consider providing async-first API for better I/O performance
- Use `asyncio.gather()` for concurrent operations

### Module System
- Use standard Python package structure
- Absolute imports from package root
- Proper `__init__.py` with `__all__` for public API
- Consider namespace packages if needed

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

## Estimated Complexity

**Lines of Code:** ~8,000-12,000 LOC (Python is typically more concise than Java)

**Module Priority:**
1. **cheap.core** (highest) - Foundation for everything else
2. **cheap.json** - Needed for testing/debugging
3. **cheap.db** - Can follow after core is stable

**Risk Areas:**
- Ensuring type safety with mypy in complex generic scenarios
- Database async patterns and connection management
- Performance compared to Java (may need optimization)
- Memory usage with large datasets (Python has higher overhead)

**Python-Specific Considerations:**
- GIL (Global Interpreter Lock) may limit CPU-bound parallelism
- Consider `multiprocessing` for CPU-bound operations
- Memory usage is higher than Java; monitor carefully
- Dynamic typing requires discipline with type hints

---

## Additional Recommendations

### Code Quality Tools
- **ruff:** Modern, fast linter and formatter (replaces black, isort, flake8)
- **mypy:** Static type checker with strict mode
- **pytest:** Testing framework with rich plugin ecosystem
- **pre-commit:** Git hooks for code quality checks

### Development Workflow
- Use `poetry` or `hatch` for dependency management
- Use `tox` or `nox` for testing across Python versions
- Use GitHub Actions or similar for CI/CD
- Use `coverage.py` (via pytest-cov) for test coverage

### Optional Enhancements
- **Pydantic V2:** For runtime validation and serialization (very fast)
- **SQLAlchemy 2.0:** For database abstraction layer
- **FastAPI integration:** If building REST API (cheapd module)
- **Type stubs:** For better IDE support and type checking

---

This plan provides a structured approach to porting the Cheap Java project to Python while leveraging Python's strengths (dynamic typing, async support, simpler syntax) and maintaining architectural integrity.
