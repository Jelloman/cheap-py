"""MariaDB/MySQL schema management for Cheap data model."""

from __future__ import annotations

import aiomysql

# Core schema DDL
SCHEMA_DDL = """
-- MariaDB DDL for Cheap Data Model
-- Represents the core Cheap model: Catalog, Hierarchy, Entity, Aspect, Property

-- ========== CORE CHEAP ELEMENT TABLES ==========

CREATE TABLE IF NOT EXISTS aspect_def (
  aspect_def_id CHAR(36) PRIMARY KEY,
  name TEXT NOT NULL,
  hash_version BIGINT,
  is_readable BOOLEAN NOT NULL DEFAULT true,
  is_writable BOOLEAN NOT NULL DEFAULT true,
  can_add_properties BOOLEAN NOT NULL DEFAULT false,
  can_remove_properties BOOLEAN NOT NULL DEFAULT false,
  UNIQUE KEY unique_aspect_def_name (name(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS property_def (
  aspect_def_id CHAR(36) NOT NULL,
  name TEXT NOT NULL,
  property_index INTEGER NOT NULL,
  property_type VARCHAR(3) NOT NULL CHECK (property_type IN (
    'INT', 'FLT', 'BLN', 'STR', 'TXT', 'BGI', 'BGF',
    'DAT', 'URI', 'UID', 'CLB', 'BLB'
  )),
  default_value TEXT,
  has_default_value BOOLEAN NOT NULL DEFAULT false,
  is_readable BOOLEAN NOT NULL DEFAULT true,
  is_writable BOOLEAN NOT NULL DEFAULT true,
  is_nullable BOOLEAN NOT NULL DEFAULT true,
  is_multivalued BOOLEAN NOT NULL DEFAULT false,
  PRIMARY KEY (aspect_def_id, name(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS catalog (
  catalog_id CHAR(36) PRIMARY KEY,
  species VARCHAR(10) NOT NULL CHECK (species IN ('SOURCE', 'SINK', 'MIRROR', 'CACHE', 'CLONE', 'FORK')),
  uri TEXT,
  upstream_catalog_id CHAR(36),
  version_number BIGINT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS catalog_aspect_def (
  catalog_id CHAR(36) NOT NULL,
  aspect_def_id CHAR(36) NOT NULL,
  PRIMARY KEY (catalog_id, aspect_def_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS hierarchy (
  catalog_id CHAR(36) NOT NULL,
  name TEXT NOT NULL,
  hierarchy_type VARCHAR(2) NOT NULL CHECK (hierarchy_type IN ('EL', 'ES', 'ED', 'ET', 'AM')),
  version_number BIGINT NOT NULL DEFAULT 0,
  PRIMARY KEY (catalog_id, name(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS aspect (
  entity_id CHAR(36) NOT NULL,
  aspect_def_id CHAR(36) NOT NULL,
  catalog_id CHAR(36) NOT NULL,
  hierarchy_name TEXT NOT NULL,
  PRIMARY KEY (entity_id, aspect_def_id, catalog_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========== PROPERTY VALUE STORAGE ==========

CREATE TABLE IF NOT EXISTS property_value (
  entity_id CHAR(36) NOT NULL,
  aspect_def_id CHAR(36) NOT NULL,
  catalog_id CHAR(36) NOT NULL,
  property_name TEXT NOT NULL,
  property_index INTEGER NOT NULL,
  value_index INTEGER NOT NULL DEFAULT 0,
  value_text TEXT,
  value_binary LONGBLOB,
  PRIMARY KEY (entity_id, aspect_def_id, catalog_id, property_name(255), value_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========== HIERARCHY CONTENT TABLES ==========

CREATE TABLE IF NOT EXISTS hierarchy_entity_list (
  catalog_id CHAR(36) NOT NULL,
  hierarchy_name TEXT NOT NULL,
  entity_id CHAR(36) NOT NULL,
  list_order INTEGER NOT NULL,
  PRIMARY KEY (catalog_id, hierarchy_name(255), list_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS hierarchy_entity_set (
  catalog_id CHAR(36) NOT NULL,
  hierarchy_name TEXT NOT NULL,
  entity_id CHAR(36) NOT NULL,
  set_order INTEGER,
  PRIMARY KEY (catalog_id, hierarchy_name(255), entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS hierarchy_entity_directory (
  catalog_id CHAR(36) NOT NULL,
  hierarchy_name TEXT NOT NULL,
  entity_key TEXT NOT NULL,
  entity_id CHAR(36) NOT NULL,
  dir_order INTEGER NOT NULL,
  PRIMARY KEY (catalog_id, hierarchy_name(255), entity_key(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS hierarchy_entity_tree_node (
  node_id CHAR(36) PRIMARY KEY,
  catalog_id CHAR(36) NOT NULL,
  hierarchy_name TEXT NOT NULL,
  parent_node_id CHAR(36),
  node_key TEXT,
  entity_id CHAR(36),
  node_path TEXT,
  tree_order INTEGER NOT NULL,
  UNIQUE KEY unique_tree_node (catalog_id, hierarchy_name(255), parent_node_id, node_key(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS hierarchy_aspect_map (
  catalog_id CHAR(36) NOT NULL,
  hierarchy_name TEXT NOT NULL,
  entity_id CHAR(36) NOT NULL,
  aspect_def_id CHAR(36) NOT NULL,
  map_order INTEGER NOT NULL,
  PRIMARY KEY (catalog_id, hierarchy_name(255), entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# Foreign key constraints DDL
FOREIGN_KEYS_DDL = """
-- PropertyDef foreign keys
ALTER TABLE property_def
    ADD CONSTRAINT fk_property_def_aspect_def FOREIGN KEY (aspect_def_id)
        REFERENCES aspect_def(aspect_def_id) ON DELETE CASCADE;

-- Catalog-AspectDef link table foreign keys
ALTER TABLE catalog_aspect_def
    ADD CONSTRAINT fk_catalog_aspect_def_catalog FOREIGN KEY (catalog_id)
        REFERENCES catalog(catalog_id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_catalog_aspect_def_aspect_def FOREIGN KEY (aspect_def_id)
        REFERENCES aspect_def(aspect_def_id) ON DELETE CASCADE;

-- Hierarchy foreign keys
ALTER TABLE hierarchy
    ADD CONSTRAINT fk_hierarchy_catalog FOREIGN KEY (catalog_id)
        REFERENCES catalog(catalog_id) ON DELETE CASCADE;

-- Aspect foreign keys
ALTER TABLE aspect
    ADD CONSTRAINT fk_aspect_aspect_def FOREIGN KEY (aspect_def_id)
        REFERENCES aspect_def(aspect_def_id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_aspect_catalog FOREIGN KEY (catalog_id)
        REFERENCES catalog(catalog_id) ON DELETE CASCADE;

-- Property value foreign keys
ALTER TABLE property_value
    ADD CONSTRAINT fk_property_value_aspect FOREIGN KEY (entity_id, aspect_def_id, catalog_id)
        REFERENCES aspect(entity_id, aspect_def_id, catalog_id) ON DELETE CASCADE;

-- Hierarchy tree node foreign keys
ALTER TABLE hierarchy_entity_tree_node
    ADD CONSTRAINT fk_hierarchy_entity_tree_parent FOREIGN KEY (parent_node_id)
        REFERENCES hierarchy_entity_tree_node(node_id) ON DELETE CASCADE;

-- Hierarchy aspect map foreign keys
ALTER TABLE hierarchy_aspect_map
    ADD CONSTRAINT fk_hierarchy_aspect_map_aspect_def FOREIGN KEY (aspect_def_id)
        REFERENCES aspect_def(aspect_def_id),
    ADD CONSTRAINT fk_hierarchy_aspect_map_aspect FOREIGN KEY (entity_id, aspect_def_id, catalog_id)
        REFERENCES aspect(entity_id, aspect_def_id, catalog_id) ON DELETE CASCADE;
"""

# Audit columns DDL
AUDIT_DDL = """
-- MariaDB Audit DDL for Cheap Data Model
-- Adds audit columns (created_at, updated_at) to track data changes

-- ========== ADD AUDIT COLUMNS TO DEFINITION TABLES ==========

-- Add audit columns to aspect_def
ALTER TABLE aspect_def
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);

-- Add audit columns to property_def
ALTER TABLE property_def
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);

-- ========== ADD AUDIT COLUMNS TO LINK TABLES ==========

-- Add audit columns to catalog_aspect_def
ALTER TABLE catalog_aspect_def
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);

-- ========== ADD AUDIT COLUMNS TO CORE ENTITY TABLES ==========

-- Add audit columns to catalog
ALTER TABLE catalog
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);

-- Add audit columns to hierarchy
ALTER TABLE hierarchy
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);

-- Add audit columns to aspect
ALTER TABLE aspect
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);

-- ========== ADD AUDIT COLUMNS TO PROPERTY VALUE STORAGE ==========

-- Add audit columns to property_value
ALTER TABLE property_value
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);

-- ========== ADD AUDIT COLUMNS TO HIERARCHY CONTENT TABLES ==========

-- Add audit columns to hierarchy_entity_list
ALTER TABLE hierarchy_entity_list
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);

-- Add audit columns to hierarchy_entity_set
ALTER TABLE hierarchy_entity_set
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);

-- Add audit columns to hierarchy_entity_directory
ALTER TABLE hierarchy_entity_directory
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);

-- Add audit columns to hierarchy_entity_tree_node
ALTER TABLE hierarchy_entity_tree_node
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);

-- Add audit columns to hierarchy_aspect_map
ALTER TABLE hierarchy_aspect_map
ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);
"""

# Drop schema DDL
DROP_DDL = """
-- Drop all tables in reverse dependency order

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
DROP TABLE IF EXISTS catalog_aspect_def;
DROP TABLE IF EXISTS catalog;

-- Drop definition tables
DROP TABLE IF EXISTS property_def;
DROP TABLE IF EXISTS aspect_def;
"""

# Truncate data DDL
TRUNCATE_DDL = """
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE hierarchy_aspect_map WAIT 50;
TRUNCATE TABLE hierarchy_entity_tree_node WAIT 50;
TRUNCATE TABLE hierarchy_entity_directory WAIT 50;
TRUNCATE TABLE hierarchy_entity_set WAIT 50;
TRUNCATE TABLE hierarchy_entity_list WAIT 50;
TRUNCATE TABLE property_value WAIT 50;
TRUNCATE TABLE aspect WAIT 50;
TRUNCATE TABLE hierarchy WAIT 50;
TRUNCATE TABLE catalog_aspect_def WAIT 50;
TRUNCATE TABLE catalog WAIT 50;
TRUNCATE TABLE property_def WAIT 50;
TRUNCATE TABLE aspect_def WAIT 50;

SET FOREIGN_KEY_CHECKS = 1;
"""


class MariaDbSchema:
    """MariaDB/MySQL schema management utilities."""

    @staticmethod
    async def create_schema(
        conn: aiomysql.Connection,
        *,
        include_audit: bool = False,
        include_foreign_keys: bool = False,
    ) -> None:
        """Create the CHEAP schema in MariaDB/MySQL.

        Args:
            conn: Active database connection
            include_audit: If True, add audit columns (created_at, updated_at)
            include_foreign_keys: If True, add foreign key constraints
        """
        async with conn.cursor() as cur:
            # Execute core schema DDL
            await cur.execute(SCHEMA_DDL)

            # Optionally add foreign key constraints
            if include_foreign_keys:
                await cur.execute(FOREIGN_KEYS_DDL)

            # Optionally add audit columns
            if include_audit:
                await cur.execute(AUDIT_DDL)

        await conn.commit()

    @staticmethod
    async def drop_schema(conn: aiomysql.Connection) -> None:
        """Drop the CHEAP schema from MariaDB/MySQL.

        Args:
            conn: Active database connection
        """
        async with conn.cursor() as cur:
            await cur.execute(DROP_DDL)
        await conn.commit()

    @staticmethod
    async def truncate_data(conn: aiomysql.Connection) -> None:
        """Truncate all data from CHEAP tables while preserving schema.

        Args:
            conn: Active database connection
        """
        async with conn.cursor() as cur:
            await cur.execute(TRUNCATE_DDL)
        await conn.commit()

    @staticmethod
    async def schema_exists(conn: aiomysql.Connection) -> bool:
        """Check if the CHEAP schema exists.

        Args:
            conn: Active database connection

        Returns:
            True if the schema exists, False otherwise
        """
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                  AND table_name = 'aspect_def'
                """
            )
            result = await cur.fetchone()
            return bool(result and result[0] > 0)
