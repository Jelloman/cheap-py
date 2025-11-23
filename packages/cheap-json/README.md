# cheap-json

JSON serialization and deserialization library for the Cheap data model.

## Overview

This module provides high-performance JSON serialization and deserialization for CHEAP data model objects using [orjson](https://github.com/ijl/orjson).

## Features

- **High Performance**: Uses orjson for 2-5x faster serialization than standard `json` library
- **Native UUID Support**: Automatically handles `uuid.UUID` serialization/deserialization
- **Native datetime Support**: Handles `datetime` objects natively
- **Type Safe**: Full type hints throughout with basedpyright compatibility
- **Perfect Fidelity**: Round-trip serialization preserves all data

## Usage

### Serialization

```python
from cheap.json import CheapJsonSerializer
from cheap.core import PropertyDefImpl, PropertyType

prop_def = PropertyDefImpl(
    name="age",
    property_type=PropertyType.INTEGER
)

# Serialize to bytes
json_bytes = CheapJsonSerializer.to_json(prop_def)

# Serialize to string
json_str = CheapJsonSerializer.to_json_str(prop_def)

# Pretty print
json_pretty = CheapJsonSerializer.to_json_str(prop_def, pretty=True)
```

### Deserialization

```python
from cheap.json import CheapJsonDeserializer

# Deserialize PropertyDef
prop_def = CheapJsonDeserializer.from_json_property_def(json_bytes)

# Deserialize AspectDef
aspect_def = CheapJsonDeserializer.from_json_aspect_def(json_bytes)

# Deserialize Catalog
catalog = CheapJsonDeserializer.from_json_catalog(json_bytes)
```

## Supported Types

- PropertyDef
- Property
- AspectDef
- Aspect
- Entity
- HierarchyDef
- Hierarchy
- CatalogDef
- Catalog

## Dependencies

- cheap-core: Core CHEAP data model
- orjson >= 3.9.0: High-performance JSON library

## License

MIT
