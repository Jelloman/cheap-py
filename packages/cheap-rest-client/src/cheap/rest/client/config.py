"""Configuration for Cheap REST client."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CheapClientConfig(BaseSettings):
    """Configuration for Cheap REST client.

    Configuration can be provided via:
    - Constructor arguments
    - Environment variables with CHEAP_CLIENT_ prefix
    - .env file
    """

    model_config = SettingsConfigDict(
        env_prefix="CHEAP_CLIENT_",
        env_file=".env",
        case_sensitive=False,
    )

    base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL of the Cheap REST API",
    )

    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds",
        gt=0,
    )

    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=0,
    )

    retry_backoff_factor: float = Field(
        default=0.5,
        description="Exponential backoff factor for retries",
        ge=0,
    )

    # Authentication (future extension)
    api_key: str | None = Field(
        default=None,
        description="API key for authentication (if required)",
    )

    # Connection pooling
    max_connections: int = Field(
        default=100,
        description="Maximum number of connection pool connections",
        gt=0,
    )

    max_keepalive_connections: int = Field(
        default=20,
        description="Maximum number of keep-alive connections",
        gt=0,
    )
