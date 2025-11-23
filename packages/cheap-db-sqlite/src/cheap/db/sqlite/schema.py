"""SQLite schema management for the CHEAP data model."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import aiosqlite


# Main schema DDL - ported from sqlite-cheap.sql
SCHEMA_DDL = """
-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Aspect Definition Table
CREATE TABLE IF NOT EXISTS aspect_def (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    is_readable INTEGER NOT NULL DEFAULT 1 CHECK (is_readable IN (0, 1)),
    is_writable INTEGER NOT NULL DEFAULT 1 CHECK (is_writable IN (0, 1)),
    can_add_properties INTEGER NOT NULL DEFAULT 0 CHECK (can_add_properties IN (0, 1)),
    can_remove_properties INTEGER NOT NULL DEFAULT 0 CHECK (can_remove_properties IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_aspect_def_name ON aspect_def(name);

-- Property Definition Table
CREATE TABLE IF NOT EXISTS property_def (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aspect_def_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('INT', 'FLT', 'BLN', 'STR', 'TXT', 'BGI', 'BGF', 'DAT', 'URI', 'UID', 'CLB', 'BLB')),
    is_writable INTEGER NOT NULL DEFAULT 1 CHECK (is_writable IN (0, 1)),
    is_nullable INTEGER NOT NULL DEFAULT 1 CHECK (is_nullable IN (0, 1)),
    is_multivalued INTEGER NOT NULL DEFAULT 0 CHECK (is_multivalued IN (0, 1)),
    default_value TEXT,
    FOREIGN KEY (aspect_def_id) REFERENCES aspect_def(id) ON DELETE CASCADE,
    UNIQUE (aspect_def_id, name)
);

CREATE INDEX IF NOT EXISTS idx_property_def_aspect_def ON property_def(aspect_def_id);
CREATE INDEX IF NOT EXISTS idx_property_def_name ON property_def(aspect_def_id, name);

-- Catalog Table
CREATE TABLE IF NOT EXISTS catalog (
    id TEXT PRIMARY KEY,
    species TEXT NOT NULL CHECK (species IN ('SOURCE', 'SINK', 'MIRROR', 'CACHE', 'CLONE', 'FORK')),
    version TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_catalog_species ON catalog(species);

-- Catalog-AspectDef Link Table
CREATE TABLE IF NOT EXISTS catalog_aspect_def (
    catalog_id TEXT NOT NULL,
    aspect_def_id TEXT NOT NULL,
    FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE,
    FOREIGN KEY (aspect_def_id) REFERENCES aspect_def(id) ON DELETE CASCADE,
    PRIMARY KEY (catalog_id, aspect_def_id)
);

CREATE INDEX IF NOT EXISTS idx_catalog_aspect_def_catalog ON catalog_aspect_def(catalog_id);
CREATE INDEX IF NOT EXISTS idx_catalog_aspect_def_aspect ON catalog_aspect_def(aspect_def_id);

-- Hierarchy Definition Table
CREATE TABLE IF NOT EXISTS hierarchy_def (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    catalog_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('EL', 'ES', 'ED', 'ET', 'AM')),
    FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE,
    UNIQUE (catalog_id, name)
);

CREATE INDEX IF NOT EXISTS idx_hierarchy_def_catalog ON hierarchy_def(catalog_id);
CREATE INDEX IF NOT EXISTS idx_hierarchy_def_name ON hierarchy_def(catalog_id, name);

-- Entity Table
CREATE TABLE IF NOT EXISTS entity (
    id TEXT PRIMARY KEY,
    catalog_id TEXT NOT NULL,
    FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_entity_catalog ON entity(catalog_id);

-- Hierarchy Table
CREATE TABLE IF NOT EXISTS hierarchy (
    id TEXT PRIMARY KEY,
    catalog_id TEXT NOT NULL,
    hierarchy_def_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE,
    FOREIGN KEY (hierarchy_def_id) REFERENCES hierarchy_def(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hierarchy_catalog ON hierarchy(catalog_id);
CREATE INDEX IF NOT EXISTS idx_hierarchy_def ON hierarchy(hierarchy_def_id);

-- Aspect Table
CREATE TABLE IF NOT EXISTS aspect (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    aspect_def_id TEXT NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    FOREIGN KEY (aspect_def_id) REFERENCES aspect_def(id) ON DELETE CASCADE,
    UNIQUE (entity_id, aspect_def_id)
);

CREATE INDEX IF NOT EXISTS idx_aspect_entity ON aspect(entity_id);
CREATE INDEX IF NOT EXISTS idx_aspect_def ON aspect(aspect_def_id);

-- Property Value Table
CREATE TABLE IF NOT EXISTS property_value (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aspect_id INTEGER NOT NULL,
    property_def_id INTEGER NOT NULL,
    value_text TEXT,
    value_binary BLOB,
    FOREIGN KEY (aspect_id) REFERENCES aspect(id) ON DELETE CASCADE,
    FOREIGN KEY (property_def_id) REFERENCES property_def(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_property_value_aspect ON property_value(aspect_id);
CREATE INDEX IF NOT EXISTS idx_property_value_property_def ON property_value(property_def_id);
CREATE INDEX IF NOT EXISTS idx_property_value_aspect_property ON property_value(aspect_id, property_def_id);

-- Hierarchy Content: Entity List
CREATE TABLE IF NOT EXISTS hierarchy_entity_list (
    hierarchy_id TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, position)
);

CREATE INDEX IF NOT EXISTS idx_hel_hierarchy ON hierarchy_entity_list(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_hel_entity ON hierarchy_entity_list(entity_id);

-- Hierarchy Content: Entity Set
CREATE TABLE IF NOT EXISTS hierarchy_entity_set (
    hierarchy_id TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    position INTEGER,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_hes_hierarchy ON hierarchy_entity_set(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_hes_entity ON hierarchy_entity_set(entity_id);

-- Hierarchy Content: Entity Directory
CREATE TABLE IF NOT EXISTS hierarchy_entity_directory (
    hierarchy_id TEXT NOT NULL,
    key TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, key)
);

CREATE INDEX IF NOT EXISTS idx_hed_hierarchy ON hierarchy_entity_directory(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_hed_entity ON hierarchy_entity_directory(entity_id);
CREATE INDEX IF NOT EXISTS idx_hed_key ON hierarchy_entity_directory(hierarchy_id, key);

-- Hierarchy Content: Entity Tree Node
CREATE TABLE IF NOT EXISTS hierarchy_entity_tree_node (
    hierarchy_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    parent_node_id TEXT,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    -- FOREIGN KEY (parent_node_id) removed due to self-reference complexity
    PRIMARY KEY (hierarchy_id, node_id)
);

CREATE INDEX IF NOT EXISTS idx_hetn_hierarchy ON hierarchy_entity_tree_node(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_hetn_entity ON hierarchy_entity_tree_node(entity_id);
CREATE INDEX IF NOT EXISTS idx_hetn_parent ON hierarchy_entity_tree_node(parent_node_id);

-- Hierarchy Content: Aspect Map
CREATE TABLE IF NOT EXISTS hierarchy_aspect_map (
    hierarchy_id TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    aspect_id INTEGER NOT NULL,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    FOREIGN KEY (aspect_id) REFERENCES aspect(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_ham_hierarchy ON hierarchy_aspect_map(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_ham_entity ON hierarchy_aspect_map(entity_id);
CREATE INDEX IF NOT EXISTS idx_ham_aspect ON hierarchy_aspect_map(aspect_id);
"""

# Audit schema DDL - ported from sqlite-cheap-audit.sql
AUDIT_DDL = """
-- Add audit columns to definition tables
ALTER TABLE aspect_def ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE aspect_def ADD COLUMN updated_at TEXT DEFAULT (datetime('now'));

ALTER TABLE property_def ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE property_def ADD COLUMN updated_at TEXT DEFAULT (datetime('now'));

-- Catalog already has audit columns in main schema

-- Add audit columns to hierarchy
ALTER TABLE hierarchy ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE hierarchy ADD COLUMN updated_at TEXT DEFAULT (datetime('now'));

-- Add audit columns to aspect
ALTER TABLE aspect ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE aspect ADD COLUMN updated_at TEXT DEFAULT (datetime('now'));

-- Add audit columns to property_value
ALTER TABLE property_value ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE property_value ADD COLUMN updated_at TEXT DEFAULT (datetime('now'));

-- Add created_at to link tables
ALTER TABLE catalog_aspect_def ADD COLUMN created_at TEXT DEFAULT (datetime('now'));

-- Add created_at to hierarchy content tables
ALTER TABLE hierarchy_entity_list ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE hierarchy_entity_set ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE hierarchy_entity_directory ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE hierarchy_entity_tree_node ADD COLUMN created_at TEXT DEFAULT (datetime('now'));
ALTER TABLE hierarchy_aspect_map ADD COLUMN created_at TEXT DEFAULT (datetime('now'));

-- Create triggers for updated_at columns
CREATE TRIGGER IF NOT EXISTS update_aspect_def_updated_at
AFTER UPDATE ON aspect_def
FOR EACH ROW
BEGIN
    UPDATE aspect_def SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_property_def_updated_at
AFTER UPDATE ON property_def
FOR EACH ROW
BEGIN
    UPDATE property_def SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_catalog_updated_at
AFTER UPDATE ON catalog
FOR EACH ROW
BEGIN
    UPDATE catalog SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_hierarchy_updated_at
AFTER UPDATE ON hierarchy
FOR EACH ROW
BEGIN
    UPDATE hierarchy SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_aspect_updated_at
AFTER UPDATE ON aspect
FOR EACH ROW
BEGIN
    UPDATE aspect SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_property_value_updated_at
AFTER UPDATE ON property_value
FOR EACH ROW
BEGIN
    UPDATE property_value SET updated_at = datetime('now') WHERE id = NEW.id;
END;
"""

# Drop schema DDL - ported from sqlite-cheap-drop.sql
DROP_DDL = """
-- Drop triggers
DROP TRIGGER IF EXISTS update_aspect_def_updated_at;
DROP TRIGGER IF EXISTS update_property_def_updated_at;
DROP TRIGGER IF EXISTS update_catalog_updated_at;
DROP TRIGGER IF EXISTS update_hierarchy_updated_at;
DROP TRIGGER IF EXISTS update_aspect_updated_at;
DROP TRIGGER IF EXISTS update_property_value_updated_at;

-- Drop hierarchy content tables
DROP TABLE IF EXISTS hierarchy_aspect_map;
DROP TABLE IF EXISTS hierarchy_entity_tree_node;
DROP TABLE IF EXISTS hierarchy_entity_directory;
DROP TABLE IF EXISTS hierarchy_entity_set;
DROP TABLE IF EXISTS hierarchy_entity_list;

-- Drop property value storage
DROP TABLE IF EXISTS property_value;

-- Drop core entity tables
DROP TABLE IF EXISTS aspect;
DROP TABLE IF EXISTS hierarchy;
DROP TABLE IF EXISTS entity;

-- Drop link tables
DROP TABLE IF EXISTS catalog_aspect_def;

-- Drop definition tables
DROP TABLE IF EXISTS hierarchy_def;
DROP TABLE IF EXISTS property_def;
DROP TABLE IF EXISTS catalog;
DROP TABLE IF EXISTS aspect_def;
"""

# Truncate schema DDL - ported from sqlite-cheap-truncate.sql
TRUNCATE_DDL = """
-- Disable foreign keys temporarily
PRAGMA foreign_keys = OFF;

-- Delete data in reverse dependency order
DELETE FROM hierarchy_aspect_map;
DELETE FROM hierarchy_entity_tree_node;
DELETE FROM hierarchy_entity_directory;
DELETE FROM hierarchy_entity_set;
DELETE FROM hierarchy_entity_list;
DELETE FROM property_value;
DELETE FROM aspect;
DELETE FROM hierarchy;
DELETE FROM entity;
DELETE FROM catalog_aspect_def;
DELETE FROM hierarchy_def;
DELETE FROM property_def;
DELETE FROM catalog;
DELETE FROM aspect_def;

-- Re-enable foreign keys
PRAGMA foreign_keys = ON;

-- Optional: reclaim space (commented out by default for performance)
-- VACUUM;
"""


class SqliteSchema:
    """
    SQLite schema management for the CHEAP data model.

    Provides methods to create, drop, and truncate the database schema.
    Supports optional audit tracking with timestamps and triggers.
    """

    @staticmethod
    async def create_schema(conn: aiosqlite.Connection, *, include_audit: bool = False) -> None:
        """
        Create the CHEAP database schema.

        Args:
            conn: SQLite database connection.
            include_audit: If True, also create audit columns and triggers.

        Raises:
            aiosqlite.Error: If schema creation fails.
        """
        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys = ON")

        # Execute main schema DDL
        await conn.executescript(SCHEMA_DDL)

        # Optionally add audit functionality
        if include_audit:
            await conn.executescript(AUDIT_DDL)

        await conn.commit()

    @staticmethod
    async def drop_schema(conn: aiosqlite.Connection) -> None:
        """
        Drop all CHEAP database tables and triggers.

        Args:
            conn: SQLite database connection.

        Raises:
            aiosqlite.Error: If schema drop fails.
        """
        await conn.executescript(DROP_DDL)
        await conn.commit()

    @staticmethod
    async def truncate_data(conn: aiosqlite.Connection, *, vacuum: bool = False) -> None:
        """
        Truncate all data from CHEAP database tables.

        Preserves schema structure but removes all data.

        Args:
            conn: SQLite database connection.
            vacuum: If True, run VACUUM to reclaim disk space.

        Raises:
            aiosqlite.Error: If truncation fails.
        """
        await conn.executescript(TRUNCATE_DDL)

        if vacuum:
            await conn.execute("VACUUM")

        await conn.commit()

    @staticmethod
    async def schema_exists(conn: aiosqlite.Connection) -> bool:
        """
        Check if the CHEAP schema exists in the database.

        Args:
            conn: SQLite database connection.

        Returns:
            True if schema exists, False otherwise.
        """
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='catalog'"
        )
        result = await cursor.fetchone()
        await cursor.close()
        return result is not None
