"""Configuration for Cheap REST API."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseType(str, Enum):
    """Supported database backend types."""

    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MARIADB = "mariadb"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="CHEAP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API configuration
    api_title: str = "Cheap REST API"
    api_version: str = "1.0.0"
    api_description: str = "REST API for the Cheap data caching system"

    # Database configuration
    database_type: DatabaseType = Field(default=DatabaseType.SQLITE)

    # SQLite configuration
    database_path: str = "./cheap.db"

    # PostgreSQL configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "cheap"
    postgres_user: str = "cheap_user"
    postgres_password: str = ""

    # MariaDB configuration
    mariadb_host: str = "localhost"
    mariadb_port: int = 3306
    mariadb_db: str = "cheap"
    mariadb_user: str = "cheap_user"
    mariadb_password: str = ""

    # Pagination
    pagination_default_size: int = 20
    pagination_max_size: int = 100

    # Batch operations
    batch_max_size: int = 1000


# Global settings instance
settings = Settings()
