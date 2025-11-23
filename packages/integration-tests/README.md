# Cheap Integration Tests

Comprehensive integration tests for the Cheap data caching system.

## Test Categories

### Cross-Database Tests
Tests that verify consistent behavior across all database backends:
- SQLite
- PostgreSQL
- MariaDB

### End-to-End Tests
Full system integration tests:
- REST API → Database → Response cycle
- REST Client → REST API → Database integration
- Complex multi-entity scenarios

### Performance Tests
Baseline performance measurements:
- Bulk operations
- Query performance
- Concurrent access patterns

## Running Tests

### All Integration Tests
```bash
pytest tests/
```

### Specific Test Categories
```bash
# Cross-database tests only
pytest -m database tests/

# End-to-end tests only
pytest -m e2e tests/

# Performance tests
pytest -m performance tests/
```

### With Docker Containers
```bash
# Using testcontainers (requires Docker)
TESTCONTAINERS_ENABLED=1 pytest tests/
```

## Test Markers

- `integration`: General integration tests
- `e2e`: End-to-end system tests
- `database`: Database-specific tests
- `performance`: Performance/benchmark tests

## Requirements

- Docker (for testcontainers)
- PostgreSQL client libraries
- MariaDB client libraries
