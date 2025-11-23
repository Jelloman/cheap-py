# cheap-rest-client

Python REST client for the Cheap REST API.

## Features

- **Type-safe API** using core model objects
- **Sync and async** client variants
- **Automatic retries** with exponential backoff
- **Comprehensive exception handling**
- **Connection pooling** for performance
- **Configuration** via environment variables or direct parameters

## Installation

```bash
pip install cheap-rest-client
```

## Usage

### Synchronous Client

```python
from cheap.rest.client import CheapClient

# Create client
client = CheapClient(base_url="http://localhost:8000")

# Create a catalog
from cheap.core.catalog_species import CatalogSpecies
catalog = client.create_catalog(species=CatalogSpecies.SOURCE, version="1.0.0")
print(f"Created catalog: {catalog.catalog_id}")

# Get a catalog
catalog = client.get_catalog(catalog_id)
print(f"Catalog species: {catalog.species}")

# Delete a catalog
client.delete_catalog(catalog_id)
```

### Asynchronous Client

```python
import asyncio
from cheap.rest.client import AsyncCheapClient

async def main():
    # Create async client
    async with AsyncCheapClient(base_url="http://localhost:8000") as client:
        # Create a catalog
        catalog = await client.create_catalog(
            species=CatalogSpecies.SOURCE,
            version="1.0.0"
        )
        print(f"Created catalog: {catalog.catalog_id}")

        # Get a catalog
        catalog = await client.get_catalog(catalog.catalog_id)
        print(f"Catalog species: {catalog.species}")

asyncio.run(main())
```

## Error Handling

```python
from cheap.rest.client import CheapClient
from cheap.rest.client.exceptions import (
    CheapRestNotFoundException,
    CheapRestBadRequestException,
    CheapRestClientException,
)

client = CheapClient(base_url="http://localhost:8000")

try:
    catalog = client.get_catalog(invalid_id)
except CheapRestNotFoundException:
    print("Catalog not found")
except CheapRestBadRequestException as e:
    print(f"Bad request: {e.message}")
except CheapRestClientException as e:
    print(f"Client error: {e.message}")
```

## Configuration

```python
from cheap.rest.client import CheapClient

client = CheapClient(
    base_url="http://localhost:8000",
    timeout=30.0,  # Request timeout in seconds
    max_retries=3,  # Number of retries
    retry_backoff_factor=0.5,  # Exponential backoff factor
)
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Type check
basedpyright

# Format code
ruff format

# Lint code
ruff check
```
