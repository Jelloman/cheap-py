"""Nox configuration for multi-version testing."""

import nox

# Supported Python versions
PYTHON_VERSIONS = ["3.11", "3.12", "3.13", "3.14"]

# Default sessions to run
nox.options.sessions = ["tests", "typecheck", "lint"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run unit tests for all packages across multiple Python versions."""
    session.install(
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-asyncio>=0.21.0",
        "pytest-xdist>=3.3.0",
    )

    # Install all packages in development mode
    session.install("-e", "packages/cheap-core", silent=False)
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


@nox.session(python="3.12")
def typecheck(session: nox.Session) -> None:
    """Run Pyright type checking."""
    session.install("basedpyright>=1.34.0")

    # Install packages for type checking
    session.install("-e", "packages/cheap-core", silent=False)

    # Run basedpyright (uses pyrightconfig.json to determine what to check)
    # This will check both packages/*/src and noxfile.py
    session.run("basedpyright", *session.posargs)


@nox.session(python="3.12")
def lint(session: nox.Session) -> None:
    """Run ruff linting and formatting checks."""
    session.install("ruff>=0.2.0")

    # Check code style
    session.run("ruff", "check", "packages/", *session.posargs)

    # Check formatting
    session.run("ruff", "format", "--check", "packages/", *session.posargs)


@nox.session(python="3.12")
def format(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff>=0.2.0")

    # Format code
    session.run("ruff", "format", "packages/", *session.posargs)


@nox.session(python="3.12")
def integration_tests(session: nox.Session) -> None:
    """Run integration tests."""
    session.install(
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "testcontainers>=3.7.0",
    )

    # Install all packages
    session.install("-e", "packages/cheap-core", silent=False)
    # Additional packages will be added as they're implemented

    # Run integration tests
    session.run(
        "pytest",
        "-v",
        "packages/integration-tests/",
        *session.posargs,
    )


@nox.session(python="3.12")
def docker_integration_tests(session: nox.Session) -> None:
    """Run dockerized integration tests."""
    session.install(
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "testcontainers>=3.7.0",
    )

    # Install all packages
    session.install("-e", "packages/cheap-core", silent=False)
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


@nox.session(python="3.12")
def docs(session: nox.Session) -> None:
    """Build documentation (placeholder for future)."""
    session.install("sphinx>=7.0.0")
    session.run("echo", "Documentation build not yet implemented")
