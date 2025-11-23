# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CheapPy is a Python port of the Cheap Java project - a git-like system for structured data based on the CHEAP model (Catalog, Hierarchy, Entity, Aspect, Property). This is a comprehensive data caching system organized into 8 modules across three functional categories: core persistence layers, REST API infrastructure, and testing frameworks.

**Source Repository**: The Java implementation is at https://github.com/Jelloman/cheap

**Important**: All porting work references the **Java implementation only** from the repository above. The TypeScript port (cheap-ts) is not mature/well-tested and should not be used as an implementation reference.

## Development Commands

### Initial Setup
```bash
# Sync workspace and install all dependencies
uv sync --extra dev

# This installs:
# - cheap-core (and future workspace packages)
# - All dev dependencies (pytest, pyright, ruff, etc.)
```

### Testing
```bash
# Run all tests (unit tests, type checking, linting)
nox

# Run tests for all Python versions (3.11, 3.12, 3.13, 3.14)
nox -s tests

# Run tests for specific Python version
nox -s tests-3.12

# Run single test file with uv
uv run pytest packages/cheap-core/tests/test_property_type.py -v

# Run single test file with nox
nox -s tests -- packages/cheap-core/tests/test_property_type.py

# Run with coverage
uv run pytest -v --cov=packages --cov-report=term-missing packages/
```

### Type Checking
```bash
# Run basedpyright type checking (strict mode)
nox -s typecheck

# Type check all configured files (packages + noxfile.py)
uv run basedpyright

# Type check specific package with uv
uv run basedpyright packages/cheap-core/

# Type check noxfile.py
uv run basedpyright noxfile.py
```

### Linting and Formatting
```bash
# Run ruff linting
nox -s lint

# Format code with ruff
nox -s format

# Check formatting without modifying with uv
uv run ruff format --check packages/

# Lint with uv
uv run ruff check packages/
```

### Integration Tests
```bash
# Run integration tests (when implemented)
nox -s integration_tests

# Run Docker-based integration tests (when implemented)
nox -s docker_integration_tests
```

## Architecture

### CHEAP Model Components

The system implements five core abstractions:

1. **Catalog**: Storage container for entities and hierarchies - analogous to a database or repository
2. **Hierarchy**: Organizational structures that define relationships between entities:
   - **List**: Ordered sequence of entities
   - **Set**: Unordered collection of unique entities
   - **Directory**: Key-value mapping from strings to entities
   - **Tree**: Hierarchical parent-child relationships
   - **AspectMap**: Maps entities to specific aspects
3. **Entity**: Core data object with a unique UUID, analogous to a row/document/node
4. **Aspect**: Named group of related properties attached to an entity (e.g., "contact_info", "metadata")
5. **Property**: Individual typed data value within an aspect (e.g., name: "John", age: 30)

### Module Structure

This is a monorepo with 8 packages (only cheap-core currently implemented):

```
packages/
├── cheap-core/           # Core protocols and implementations (currently in progress)
├── cheap-json/           # JSON serialization with orjson (planned)
├── cheap-db-sqlite/      # SQLite persistence (planned)
├── cheap-db-postgres/    # PostgreSQL persistence (planned)
├── cheap-db-mariadb/     # MariaDB persistence (planned)
├── cheap-rest/           # REST API with FastAPI (planned)
├── cheap-rest-client/    # Python REST client (planned)
└── integration-tests/    # Cross-database integration tests (planned)
```

### Dependency Graph
```
cheap-core (foundation)
    ↓
cheap-json
    ↓
cheap-db-{sqlite,postgres,mariadb}
    ↓
cheap-rest
    ↓
cheap-rest-client
    ↓
integration-tests
```

## Type System Architecture

### Protocols Over ABC
This codebase uses **`typing.Protocol`** for interface definitions (structural typing) rather than Abstract Base Classes (nominal typing):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Entity(Protocol):
    @property
    def id(self) -> UUID: ...

    @property
    def aspects(self) -> dict[str, Aspect]: ...
```

Benefits:
- Duck typing support - any object with matching methods satisfies the protocol
- No inheritance required
- Better separation of interface from implementation
- More Pythonic than Java-style interfaces

### Strict Type Checking
- **basedpyright** (a pyright fork) runs in strict mode (see `pyrightconfig.json`)
- Type checks both package sources (`packages/*/src`) and build scripts (`noxfile.py`)
- All code must have complete type annotations
- Use `typing.Self` (Python 3.11+) for builder pattern return types
- Use `typing.Final` for constants
- Use `typing.ClassVar` for class variables
- Zero type errors required before code is merged

### Type Mapping from Java

| Java Pattern | Python Implementation |
|--------------|----------------------|
| Interface + Implementation | `Protocol` + concrete class |
| `<T extends Foo>` | `TypeVar('T', bound=Foo)` |
| `@NotNull` / `@Nullable` | Non-optional / `Optional[T]` or `T \| None` |
| Lombok getters/setters | `@property` or `@dataclass` |
| Java Reflection | `inspect` module, `__annotations__` |
| `Enum` | `enum.Enum` or `enum.StrEnum` |
| `UUID` | `uuid.UUID` |
| `ZonedDateTime` | `datetime.datetime` with `zoneinfo` |
| `BigDecimal` | `decimal.Decimal` |
| `BigInteger` | `int` (unlimited precision in Python) |

## Implementation Standards

### Dataclasses for Data Types
Prefer `@dataclass` for implementation classes:
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class EntityImpl:
    id: UUID
    aspects: dict[str, Aspect]
```

- Use `frozen=True` for immutable classes
- Use `slots=True` (Python 3.10+) for memory efficiency
- Always include complete type hints for all fields

### Property Types
The `PropertyType` enum defines supported data types:
- Numeric: `INTEGER`, `FLOAT`, `BIG_INTEGER`, `BIG_DECIMAL`
- Boolean: `BOOLEAN`
- String: `STRING`, `TEXT`
- DateTime: `DATE_TIME`
- Special: `URI`, `UUID`
- Binary: `CLOB`, `BLOB`

### Immutability Strategy
- Use `@dataclass(frozen=True)` for immutable dataclasses
- Use `tuple` instead of `list` for immutable sequences
- Use `frozenset` instead of `set` for immutable sets
- Consider `frozendict` library for immutable dictionaries (if needed)

## Build System

### UV Workspace
This project uses **uv** for fast dependency management and **Hatch** for building:
- Single `pyproject.toml` at root defines the workspace
- `[tool.uv.workspace]` with `members = ["packages/*"]` declares workspace packages
- Each package has its own `pyproject.toml`
- Run `uv sync --extra dev` to install all workspace packages and dev dependencies
- Use `uv run <command>` to run commands in the workspace environment

**Note**: The root package (`cheap-py`) is a virtual workspace coordinator:
- Contains a dummy `src/cheap_py/` directory to satisfy hatch (ignored in git)
- Lists workspace packages as dependencies
- Should not be installed directly - use `uv sync` instead

### Hatch Monorepo
**Hatch** handles building and packaging:
- Each package can be built independently with `hatch build`
- Shared configuration for tooling (ruff, pytest, coverage)

### Nox Multi-Version Testing
**Nox** handles testing across Python 3.11, 3.12, 3.13, 3.14:
- Define test sessions in `noxfile.py`
- Uses `uv` as the virtual environment backend (`nox.options.default_venv_backend = "uv"`)
- This allows nox to use uv-managed Python installations automatically
- Separate sessions for: tests, typecheck, lint, format
- Integration tests use Python 3.12 only

## Key Dependencies

### Current Dependencies
- **pytest** - Testing framework with fixtures
- **pytest-cov** - Coverage reporting
- **pytest-asyncio** - Async test support
- **pytest-xdist** - Parallel test execution
- **basedpyright** - Static type checker (pyright fork, strict mode)
- **nox** - Multi-version testing automation
- **ruff** - Fast linter and formatter

### Planned Dependencies (for future modules)
- **orjson** - High-performance JSON with native UUID/datetime support (for cheap-json)
- **psycopg3** - Modern PostgreSQL driver with async support (for cheap-db-postgres)
- **aiosqlite** - Async SQLite driver (for cheap-db-sqlite)
- **PyMySQL** or **mysql-connector-python** - MySQL/MariaDB drivers (for cheap-db-mariadb)
- **FastAPI** - Modern async web framework (for cheap-rest)
- **httpx** - Modern HTTP client with async support (for cheap-rest-client)
- **testcontainers-python** - Docker containers for integration tests

## Testing Patterns

### Test Organization
- Tests mirror source structure in each package's `tests/` directory
- Use pytest fixtures for common setup
- Type hint all test functions with `-> None`
- Use descriptive test names: `test_<what>_<scenario>_<expected>`

### Example Test Pattern
```python
class TestPropertyType:
    """Test suite for PropertyType enum."""

    def test_enum_values(self) -> None:
        """Test that all expected enum values exist."""
        assert PropertyType.INTEGER.value == "INTEGER"
```

## Current Development Status

**Phase 2.3 Complete** - Basic implementations of core protocols:
- ✅ Type system & enums (PropertyType, HierarchyType, CatalogSpecies)
- ✅ Model protocols (Entity, Aspect, Property, Hierarchy, Catalog)
- ✅ Basic implementations (EntityImpl, AspectImpl, etc.)
- 🚧 Phase 2.4 - Reflection-based implementations (next)

See `INITIAL_PLAN.md` for complete porting plan across all 8 modules.

## Code Style

### Imports
- Use absolute imports: `from cheap.core.entity import Entity`
- Group imports: stdlib → third-party → local
- Use `from __future__ import annotations` for forward references

### Line Length
- Max line length: 100 characters (ruff configured)
- Let ruff handle formatting automatically

### Documentation
- Use Google-style docstrings
- Document all public APIs with type information
- Include examples for complex functionality

## CI/CD

### GitHub Actions Workflows
Three workflows in `.github/workflows/`:

1. **build-cheap-python.yml** - Main CI pipeline
   - Runs on push to package paths
   - Tests on Python 3.10, 3.11, 3.12, 3.13
   - Pyright type checking
   - Ruff linting
   - Coverage reporting

2. **integration-tests.yml** - Integration tests (manual dispatch)
   - Tests with SQLite, PostgreSQL, MariaDB
   - Uses testcontainers for databases

3. **docker-integration-tests.yml** - Dockerized integration tests (manual dispatch)
   - Full stack testing with real databases
   - REST API with all backends

## Common Development Workflows

### Adding a New Protocol
1. Create protocol in appropriate module (e.g., `cheap/core/`)
2. Use `@runtime_checkable` decorator
3. Add complete type hints for all methods
4. Use `Protocol` as base, not ABC
5. Run `nox -s typecheck` to verify

### Adding an Implementation
1. Create implementation class in `*_impl.py` file
2. Use `@dataclass` with appropriate flags
3. Implement protocol methods with full type hints
4. Add unit tests in `tests/test_*.py`
5. Run `nox` to verify all checks pass

### Fixing Type Errors
1. Run `nox -s typecheck` or `uv run basedpyright` to see errors
2. Add missing type hints
3. Use `typing.cast()` only when necessary
4. Avoid `# type: ignore` - fix the underlying issue
5. Check `pyrightconfig.json` for strict mode settings
6. Remember: type checking applies to both package code and `noxfile.py`

### Committing Code
**CRITICAL**: Always run formatting before committing to ensure CI checks pass:

```bash
# 1. Format code with ruff (REQUIRED before every commit)
nox -s format
# or directly: uv run ruff format packages/

# 2. Run type checking
nox -s typecheck

# 3. Run tests
nox -s tests

# 4. Stage and commit changes
git add <files>
git commit -m "Your commit message"

# 5. Push to remote
git push -u origin <branch-name>
```

**Pre-Commit Checklist**:
- ✓ Run `nox -s format` to auto-format all code
- ✓ Run `nox -s typecheck` to verify no type errors
- ✓ Run `nox -s tests` to ensure all tests pass
- ✓ All three must pass before committing

**Why This Matters**: GitHub Actions runs ruff linting and formatting checks. Code that hasn't been formatted will fail CI, blocking merges. Running `nox -s format` automatically fixes formatting issues before they reach CI.

## Package Installation

### Install Workspace (Recommended)
```bash
# Install all workspace packages and dev dependencies
uv sync --extra dev

# Install without dev dependencies
uv sync
```

### Install Specific Package Only
```bash
# Install cheap-core in editable mode with pip
pip install -e "packages/cheap-core[dev]"

# Or use uv
uv pip install -e "packages/cheap-core[dev]"
```
