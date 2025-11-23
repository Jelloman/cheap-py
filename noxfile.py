"""Nox configuration for multi-version testing."""

import nox

# Supported Python versions
# old PYTHON_VERSIONS "3.11", "3.12", "3.13", "3.14"
PYTHON_VERSIONS = ["3.13"]


# Use uv as the default virtual environment backend
# This allows nox to use uv-managed Python installations
nox.options.default_venv_backend = "uv"

# Default sessions to run
nox.options.sessions = ["tests", "typecheck", "lint"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run unit tests for all packages across multiple Python versions."""
    session.install(
        "pytest>=9.0.1",
        "pytest-cov>=7.0.0",
        "pytest-asyncio>=1.3.0",
        "pytest-xdist>=3.8.0",
        "httpx>=0.27.0",  # Required for FastAPI TestClient
    )

    # Install all packages in development mode
    session.install("-e", "packages/cheap-core", silent=False)
    session.install("-e", "packages/cheap-json", silent=False)
    session.install("-e", "packages/cheap-db-sqlite", silent=False)
    session.install("-e", "packages/cheap-db-postgres", silent=False)
    session.install("-e", "packages/cheap-db-mariadb", silent=False)
    session.install("-e", "packages/cheap-rest", silent=False)
    # Additional packages will be added as they're implemented

    # Run tests with coverage
    session.run(
        "pytest",
        "-v",
        "--cov=packages",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "packages/",
        *session.posargs,
    )


@nox.session(python="3.13")
def typecheck(session: nox.Session) -> None:
    """Run Pyright type checking."""
    session.install("basedpyright>=1.34.0")

    # Install packages for type checking
    session.install("-e", "packages/cheap-core", silent=False)
    session.install("-e", "packages/cheap-json", silent=False)
    session.install("-e", "packages/cheap-db-sqlite", silent=False)
    session.install("-e", "packages/cheap-db-postgres", silent=False)
    session.install("-e", "packages/cheap-db-mariadb", silent=False)
    session.install("-e", "packages/cheap-rest", silent=False)

    # Run basedpyright (uses pyrightconfig.json to determine what to check)
    # This will check both packages/*/src and noxfile.py
    session.run("basedpyright", *session.posargs)


@nox.session(python="3.13")
def lint(session: nox.Session) -> None:
    """Run ruff linting and formatting checks."""
    session.install("ruff>=0.2.0")

    # Check code style
    session.run("ruff", "check", "packages/", *session.posargs)

    # Check formatting
    session.run("ruff", "format", "--check", "packages/", *session.posargs)


@nox.session(python="3.13")
def format(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff>=0.2.0")

    # Format code
    session.run("ruff", "format", "packages/", *session.posargs)


@nox.session(python="3.13")
def integration_tests(session: nox.Session) -> None:
    """Run integration tests."""
    session.install(
        "pytest>=9.0.1",
        "pytest-asyncio>=1.3.0",
        "testcontainers>=3.7.0",
    )

    # Install all packages
    session.install("-e", "packages/cheap-core", silent=False)
    session.install("-e", "packages/cheap-json", silent=False)
    session.install("-e", "packages/cheap-db-sqlite", silent=False)
    session.install("-e", "packages/cheap-db-postgres", silent=False)
    session.install("-e", "packages/cheap-db-mariadb", silent=False)
    session.install("-e", "packages/cheap-rest", silent=False)
    # Additional packages will be added as they're implemented

    # Run integration tests
    session.run(
        "pytest",
        "-v",
        "packages/integration-tests/",
        *session.posargs,
    )


@nox.session(python="3.13")
def docker_integration_tests(session: nox.Session) -> None:
    """Run dockerized integration tests."""
    session.install(
        "pytest>=9.0.1",
        "pytest-asyncio>=1.3.0",
        "testcontainers>=4.13.3",
    )

    # Install all packages
    session.install("-e", "packages/cheap-rest", silent=False)
    session.install("-e", "packages/cheap-core", silent=False)
    session.install("-e", "packages/cheap-json", silent=False)
    session.install("-e", "packages/cheap-db-sqlite", silent=False)
    session.install("-e", "packages/cheap-db-postgres", silent=False)
    session.install("-e", "packages/cheap-db-mariadb", silent=False)
    # Additional packages will be added as they're implemented

    # Run Docker-based integration tests
    session.run(
        "pytest",
        "-v",
        "-m",
        "docker",
        "packages/integration-tests/",
        *session.posargs,
    )


@nox.session(python="3.13")
def docs(session: nox.Session) -> None:
    """Build documentation (placeholder for future)."""
    session.install("sphinx>=8.2.3")
    session.run("echo", "Documentation build not yet implemented")
