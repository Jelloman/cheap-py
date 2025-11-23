# cheap-rest

REST API module for the Cheap data model using FastAPI.

## Features

- **FastAPI Framework**: Modern, async Python web framework
- **Automatic OpenAPI Documentation**: Interactive docs at `/docs` and `/redoc`
- **Multi-Database Support**: SQLite, PostgreSQL, and MariaDB backends
- **Type-Safe**: Full Pydantic validation and type hints
- **Async/Await**: Non-blocking database operations
- **Health Checks**: Built-in health endpoint

## Installation

```bash
pip install cheap-rest
```

## Quick Start

### Running the Server

```bash
# Development mode with auto-reload
uvicorn cheap.rest.main:app --reload

# Production mode
cheap-rest

# Custom host/port
uvicorn cheap.rest.main:app --host 0.0.0.0 --port 8000
```

### Configuration

Configure via environment variables:

```bash
# Database backend (sqlite, postgres, mariadb)
export CHEAP_DATABASE_TYPE=sqlite
export CHEAP_DATABASE_PATH=./cheap.db

# Or for PostgreSQL
export CHEAP_DATABASE_TYPE=postgres
export CHEAP_POSTGRES_HOST=localhost
export CHEAP_POSTGRES_PORT=5432
export CHEAP_POSTGRES_DB=cheap
export CHEAP_POSTGRES_USER=cheap_user
export CHEAP_POSTGRES_PASSWORD=secret

# API settings
export CHEAP_API_TITLE="Cheap REST API"
export CHEAP_API_VERSION="1.0.0"
export CHEAP_PAGINATION_DEFAULT_SIZE=20
export CHEAP_PAGINATION_MAX_SIZE=100
```

## API Endpoints

### Health Check

```
GET /health - Health check endpoint
```

### Catalog Management

```
POST   /api/catalog              - Create new catalog
GET    /api/catalog              - List catalogs (paginated)
GET    /api/catalog/{catalogId}  - Get catalog by ID
DELETE /api/catalog/{catalogId}  - Delete catalog
```

### AspectDef Management

```
POST   /api/catalog/{catalogId}/aspect-defs                   - Create AspectDef
GET    /api/catalog/{catalogId}/aspect-defs                   - List AspectDefs
GET    /api/catalog/{catalogId}/aspect-defs/{aspectDefName}   - Get AspectDef
```

## Interactive Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Examples

### Create a Catalog

```bash
curl -X POST "http://localhost:8000/api/catalog" \
  -H "Content-Type: application/json" \
  -d '{
    "species": "SOURCE",
    "version": "1.0.0"
  }'
```

### List Catalogs

```bash
curl "http://localhost:8000/api/catalog?page=0&size=20"
```

### Get Catalog

```bash
curl "http://localhost:8000/api/catalog/{catalogId}"
```

## Development

### Running Tests

```bash
pytest packages/cheap-rest/tests/ -v
```

### Type Checking

```bash
basedpyright packages/cheap-rest/
```

### Formatting

```bash
ruff format packages/cheap-rest/
```

## Architecture

```
cheap-rest/
├── controllers/    # FastAPI route handlers
├── services/       # Business logic layer
├── models/         # Pydantic request/response models
├── exceptions/     # Custom exception classes
├── config.py       # Configuration management
└── main.py         # FastAPI application setup
```

## License

MIT
