"""Exception classes for Cheap REST client."""

from __future__ import annotations


class CheapRestClientException(Exception):
    """Base exception for Cheap REST client errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class CheapRestNotFoundException(CheapRestClientException):
    """Exception raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=404)


class CheapRestBadRequestException(CheapRestClientException):
    """Exception raised for bad requests (400)."""

    def __init__(self, message: str = "Bad request") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=400)


class CheapRestServerException(CheapRestClientException):
    """Exception raised for server errors (5xx)."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        """Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code (5xx)
        """
        super().__init__(message, status_code=status_code)
