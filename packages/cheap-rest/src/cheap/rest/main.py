"""Main FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from cheap.rest.config import settings
from cheap.rest.controllers.catalog import router as catalog_router
from cheap.rest.exceptions import CheapAPIException


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events.

    Args:
        _app: FastAPI application instance (unused but required by protocol)

    Yields:
        None
    """
    # Startup
    print(f"Starting Cheap REST API - Database: {settings.database_type.value}")
    yield
    # Shutdown
    print("Shutting down Cheap REST API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        lifespan=lifespan,
    )

    # Register routers
    app.include_router(catalog_router)

    # Exception handlers
    @app.exception_handler(CheapAPIException)
    async def cheap_exception_handler(request: Request, exc: CheapAPIException) -> JSONResponse:
        """Handle Cheap API exceptions.

        Args:
            request: HTTP request
            exc: Exception instance

        Returns:
            JSON error response
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors.

        Args:
            request: HTTP request
            exc: Validation error

        Returns:
            JSON error response
        """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "Request validation failed",
                "path": str(request.url.path),
                "errors": exc.errors(),
            },
        )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            Health status
        """
        return {
            "status": "healthy",
            "database": settings.database_type.value,
            "version": settings.api_version,
        }

    return app


# Create the application instance
app = create_app()


def run() -> None:
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "cheap.rest.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
