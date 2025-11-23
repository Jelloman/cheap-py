"""PostgreSQL schema management for the CHEAP data model."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import psycopg


# Main schema DDL - ported from postgres-cheap.sql
SCHEMA_DDL = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Aspect Definition Table
CREATE TABLE IF NOT EXISTS aspect_def (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    is_readable BOOLEAN NOT NULL DEFAULT TRUE,
    is_writable BOOLEAN NOT NULL DEFAULT TRUE,
    can_add_properties BOOLEAN NOT NULL DEFAULT FALSE,
    can_remove_properties BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_aspect_def_name ON aspect_def(name);

-- Property Definition Table
CREATE TABLE IF NOT EXISTS property_def (
    id BIGSERIAL PRIMARY KEY,
    aspect_def_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(3) NOT NULL CHECK (type IN ('INT', 'FLT', 'BLN', 'STR', 'TXT', 'BGI', 'BGF', 'DAT', 'URI', 'UID', 'CLB', 'BLB')),
    is_writable BOOLEAN NOT NULL DEFAULT TRUE,
    is_nullable BOOLEAN NOT NULL DEFAULT TRUE,
    is_multivalued BOOLEAN NOT NULL DEFAULT FALSE,
    default_value TEXT,
    FOREIGN KEY (aspect_def_id) REFERENCES aspect_def(id) ON DELETE CASCADE,
    UNIQUE (aspect_def_id, name)
);

CREATE INDEX IF NOT EXISTS idx_property_def_aspect_def ON property_def(aspect_def_id);
CREATE INDEX IF NOT EXISTS idx_property_def_name ON property_def(aspect_def_id, name);

-- Catalog Table
CREATE TABLE IF NOT EXISTS catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    species VARCHAR(10) NOT NULL CHECK (species IN ('SOURCE', 'SINK', 'MIRROR', 'CACHE', 'CLONE', 'FORK')),
    version VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_catalog_species ON catalog(species);

-- Catalog-AspectDef Link Table
CREATE TABLE IF NOT EXISTS catalog_aspect_def (
    catalog_id UUID NOT NULL,
    aspect_def_id UUID NOT NULL,
    FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE,
    FOREIGN KEY (aspect_def_id) REFERENCES aspect_def(id) ON DELETE CASCADE,
    PRIMARY KEY (catalog_id, aspect_def_id)
);

CREATE INDEX IF NOT EXISTS idx_catalog_aspect_def_catalog ON catalog_aspect_def(catalog_id);
CREATE INDEX IF NOT EXISTS idx_catalog_aspect_def_aspect ON catalog_aspect_def(aspect_def_id);

-- Hierarchy Definition Table
CREATE TABLE IF NOT EXISTS hierarchy_def (
    id BIGSERIAL PRIMARY KEY,
    catalog_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(2) NOT NULL CHECK (type IN ('EL', 'ES', 'ED', 'ET', 'AM')),
    FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE,
    UNIQUE (catalog_id, name)
);

CREATE INDEX IF NOT EXISTS idx_hierarchy_def_catalog ON hierarchy_def(catalog_id);
CREATE INDEX IF NOT EXISTS idx_hierarchy_def_name ON hierarchy_def(catalog_id, name);

-- Entity Table
CREATE TABLE IF NOT EXISTS entity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    catalog_id UUID NOT NULL,
    FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_entity_catalog ON entity(catalog_id);

-- Hierarchy Table
CREATE TABLE IF NOT EXISTS hierarchy (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    catalog_id UUID NOT NULL,
    hierarchy_def_id BIGINT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE,
    FOREIGN KEY (hierarchy_def_id) REFERENCES hierarchy_def(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hierarchy_catalog ON hierarchy(catalog_id);
CREATE INDEX IF NOT EXISTS idx_hierarchy_def ON hierarchy(hierarchy_def_id);

-- Aspect Table
CREATE TABLE IF NOT EXISTS aspect (
    id BIGSERIAL PRIMARY KEY,
    entity_id UUID NOT NULL,
    aspect_def_id UUID NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    FOREIGN KEY (aspect_def_id) REFERENCES aspect_def(id) ON DELETE CASCADE,
    UNIQUE (entity_id, aspect_def_id)
);

CREATE INDEX IF NOT EXISTS idx_aspect_entity ON aspect(entity_id);
CREATE INDEX IF NOT EXISTS idx_aspect_def ON aspect(aspect_def_id);

-- Property Value Table
CREATE TABLE IF NOT EXISTS property_value (
    id BIGSERIAL PRIMARY KEY,
    aspect_id BIGINT NOT NULL,
    property_def_id BIGINT NOT NULL,
    value_index INTEGER NOT NULL DEFAULT 0,
    value_text TEXT,
    value_binary BYTEA,
    FOREIGN KEY (aspect_id) REFERENCES aspect(id) ON DELETE CASCADE,
    FOREIGN KEY (property_def_id) REFERENCES property_def(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_property_value_aspect ON property_value(aspect_id);
CREATE INDEX IF NOT EXISTS idx_property_value_property_def ON property_value(property_def_id);
CREATE INDEX IF NOT EXISTS idx_property_value_aspect_property ON property_value(aspect_id, property_def_id);

-- Hierarchy Content: Entity List
CREATE TABLE IF NOT EXISTS hierarchy_entity_list (
    hierarchy_id UUID NOT NULL,
    entity_id UUID NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, position)
);

CREATE INDEX IF NOT EXISTS idx_hel_hierarchy ON hierarchy_entity_list(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_hel_entity ON hierarchy_entity_list(entity_id);

-- Hierarchy Content: Entity Set
CREATE TABLE IF NOT EXISTS hierarchy_entity_set (
    hierarchy_id UUID NOT NULL,
    entity_id UUID NOT NULL,
    position INTEGER,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_hes_hierarchy ON hierarchy_entity_set(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_hes_entity ON hierarchy_entity_set(entity_id);

-- Hierarchy Content: Entity Directory
CREATE TABLE IF NOT EXISTS hierarchy_entity_directory (
    hierarchy_id UUID NOT NULL,
    key VARCHAR(255) NOT NULL,
    entity_id UUID NOT NULL,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, key)
);

CREATE INDEX IF NOT EXISTS idx_hed_hierarchy ON hierarchy_entity_directory(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_hed_entity ON hierarchy_entity_directory(entity_id);
CREATE INDEX IF NOT EXISTS idx_hed_key ON hierarchy_entity_directory(hierarchy_id, key);

-- Hierarchy Content: Entity Tree Node
CREATE TABLE IF NOT EXISTS hierarchy_entity_tree_node (
    hierarchy_id UUID NOT NULL,
    node_id UUID NOT NULL,
    entity_id UUID NOT NULL,
    parent_node_id UUID,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, node_id)
);

CREATE INDEX IF NOT EXISTS idx_hetn_hierarchy ON hierarchy_entity_tree_node(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_hetn_entity ON hierarchy_entity_tree_node(entity_id);
CREATE INDEX IF NOT EXISTS idx_hetn_parent ON hierarchy_entity_tree_node(parent_node_id);

-- Hierarchy Content: Aspect Map
CREATE TABLE IF NOT EXISTS hierarchy_aspect_map (
    hierarchy_id UUID NOT NULL,
    entity_id UUID NOT NULL,
    aspect_id BIGINT NOT NULL,
    FOREIGN KEY (hierarchy_id) REFERENCES hierarchy(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE,
    FOREIGN KEY (aspect_id) REFERENCES aspect(id) ON DELETE CASCADE,
    PRIMARY KEY (hierarchy_id, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_ham_hierarchy ON hierarchy_aspect_map(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_ham_entity ON hierarchy_aspect_map(entity_id);
CREATE INDEX IF NOT EXISTS idx_ham_aspect ON hierarchy_aspect_map(aspect_id);
"""

# Audit schema DDL - ported from postgres-cheap-audit.sql
AUDIT_DDL = """
-- Add audit columns to definition tables
ALTER TABLE aspect_def
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE property_def
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Add audit columns to catalog
ALTER TABLE catalog
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Add audit columns to hierarchy
ALTER TABLE hierarchy
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Add audit columns to aspect
ALTER TABLE aspect
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Add audit columns to property_value
ALTER TABLE property_value
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Add created_at to link tables
ALTER TABLE catalog_aspect_def
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Add created_at to hierarchy content tables
ALTER TABLE hierarchy_entity_list
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE hierarchy_entity_set
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE hierarchy_entity_directory
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE hierarchy_entity_tree_node
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE hierarchy_aspect_map
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Create trigger function for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
DROP TRIGGER IF EXISTS update_aspect_def_updated_at ON aspect_def;
CREATE TRIGGER update_aspect_def_updated_at BEFORE UPDATE ON aspect_def
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_property_def_updated_at ON property_def;
CREATE TRIGGER update_property_def_updated_at BEFORE UPDATE ON property_def
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_catalog_updated_at ON catalog;
CREATE TRIGGER update_catalog_updated_at BEFORE UPDATE ON catalog
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_hierarchy_updated_at ON hierarchy;
CREATE TRIGGER update_hierarchy_updated_at BEFORE UPDATE ON hierarchy
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_aspect_updated_at ON aspect;
CREATE TRIGGER update_aspect_updated_at BEFORE UPDATE ON aspect
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_property_value_updated_at ON property_value;
CREATE TRIGGER update_property_value_updated_at BEFORE UPDATE ON property_value
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""

# Drop schema DDL - ported from postgres-cheap-drop.sql
DROP_DDL = """
-- Drop triggers
DROP TRIGGER IF EXISTS update_aspect_def_updated_at ON aspect_def;
DROP TRIGGER IF EXISTS update_property_def_updated_at ON property_def;
DROP TRIGGER IF EXISTS update_catalog_updated_at ON catalog;
DROP TRIGGER IF EXISTS update_hierarchy_updated_at ON hierarchy;
DROP TRIGGER IF EXISTS update_aspect_updated_at ON aspect;
DROP TRIGGER IF EXISTS update_property_value_updated_at ON property_value;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop hierarchy content tables
DROP TABLE IF EXISTS hierarchy_aspect_map CASCADE;
DROP TABLE IF EXISTS hierarchy_entity_tree_node CASCADE;
DROP TABLE IF EXISTS hierarchy_entity_directory CASCADE;
DROP TABLE IF EXISTS hierarchy_entity_set CASCADE;
DROP TABLE IF EXISTS hierarchy_entity_list CASCADE;

-- Drop property value storage
DROP TABLE IF EXISTS property_value CASCADE;

-- Drop core entity tables
DROP TABLE IF EXISTS aspect CASCADE;
DROP TABLE IF EXISTS hierarchy CASCADE;
DROP TABLE IF EXISTS catalog_aspect_def CASCADE;
DROP TABLE IF EXISTS catalog CASCADE;

-- Drop definition tables
DROP TABLE IF EXISTS hierarchy_def CASCADE;
DROP TABLE IF EXISTS property_def CASCADE;
DROP TABLE IF EXISTS aspect_def CASCADE;
"""

# Truncate schema DDL - ported from postgres-cheap-truncate.sql
TRUNCATE_DDL = """
-- Disable triggers to avoid foreign key issues
SET session_replication_role = replica;

-- Truncate all tables in reverse dependency order
TRUNCATE TABLE hierarchy_aspect_map CASCADE;
TRUNCATE TABLE hierarchy_entity_tree_node CASCADE;
TRUNCATE TABLE hierarchy_entity_directory CASCADE;
TRUNCATE TABLE hierarchy_entity_set CASCADE;
TRUNCATE TABLE hierarchy_entity_list CASCADE;
TRUNCATE TABLE property_value CASCADE;
TRUNCATE TABLE aspect CASCADE;
TRUNCATE TABLE hierarchy CASCADE;
TRUNCATE TABLE catalog_aspect_def CASCADE;
TRUNCATE TABLE catalog CASCADE;
TRUNCATE TABLE hierarchy_def CASCADE;
TRUNCATE TABLE property_def CASCADE;
TRUNCATE TABLE aspect_def CASCADE;

-- Re-enable triggers
SET session_replication_role = DEFAULT;
"""


class PostgresSchema:
    """
    PostgreSQL schema management for the CHEAP data model.

    Provides methods to create, drop, and truncate the database schema.
    Supports optional audit tracking with timestamps and automatic triggers.
    """

    @staticmethod
    async def create_schema(
        conn: psycopg.AsyncConnection[tuple], *, include_audit: bool = False
    ) -> None:
        """
        Create the CHEAP database schema.

        Args:
            conn: PostgreSQL database connection.
            include_audit: If True, also create audit columns and triggers.

        Raises:
            psycopg.Error: If schema creation fails.
        """
        async with conn.cursor() as cur:
            # Execute main schema DDL
            await cur.execute(SCHEMA_DDL)

            # Optionally add audit functionality
            if include_audit:
                await cur.execute(AUDIT_DDL)

        await conn.commit()

    @staticmethod
    async def drop_schema(conn: psycopg.AsyncConnection[tuple]) -> None:
        """
        Drop all CHEAP database tables, triggers, and functions.

        Args:
            conn: PostgreSQL database connection.

        Raises:
            psycopg.Error: If schema drop fails.
        """
        async with conn.cursor() as cur:
            await cur.execute(DROP_DDL)

        await conn.commit()

    @staticmethod
    async def truncate_data(conn: psycopg.AsyncConnection[tuple]) -> None:
        """
        Truncate all data from CHEAP database tables.

        Preserves schema structure but removes all data.

        Args:
            conn: PostgreSQL database connection.

        Raises:
            psycopg.Error: If truncation fails.
        """
        async with conn.cursor() as cur:
            await cur.execute(TRUNCATE_DDL)

        await conn.commit()

    @staticmethod
    async def schema_exists(conn: psycopg.AsyncConnection[tuple]) -> bool:
        """
        Check if the CHEAP schema exists in the database.

        Args:
            conn: PostgreSQL database connection.

        Returns:
            True if schema exists, False otherwise.
        """
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'catalog')"
            )
            result = await cur.fetchone()
            return result[0] if result else False
