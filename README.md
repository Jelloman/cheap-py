# CheapPy - Python Port of Cheap

A Python implementation of the CHEAP model (Catalog, Hierarchy, Entity, Aspect, Property) - a git-like system for structured data.

## Project Structure

This is a multi-package npm workspace containing:

```
cheap-py/
├── package.json              # Workspace root
├── tsconfig.base.json        # Shared TypeScript config
├── packages/
│   ├── cheap-core/           # Core CHEAP model (✓ built)
│   ├── cheap-json/           # JSON serialization (✓ built)
│   ├── cheap-db-sqlite/      # SQLite implementation (scaffolded)
│   ├── cheap-db-postgres/    # PostgreSQL implementation (scaffolded)
│   └── cheap-db-mariadb/     # MariaDB implementation (scaffolded)
```

## Status

## Building

### Build All Packages
```bash
```

## Architecture

Based on the CHEAP model:
- **Catalog**: Storage container for entities and hierarchies
- **Hierarchy**: Organizational structures (List, Set, Directory, Tree, AspectMap)
- **Entity**: Core data objects with global and local IDs
- **Aspect**: Named groups of properties
- **Property**: Individual data values with typed definitions

## Next Steps

See `INITIAL_PLAN.md` for the full porting plan. The scaffolding is complete - current phase is porting the actual Java implementation logic from the Cheap project.
