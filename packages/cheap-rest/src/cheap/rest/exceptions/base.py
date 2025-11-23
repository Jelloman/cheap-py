"""Base exception classes."""

from __future__ import annotations


class CheapAPIException(Exception):
    """Base exception for Cheap REST API."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundException(CheapAPIException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class ResourceConflictException(CheapAPIException):
    """Exception raised when a resource conflict occurs."""

    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, status_code=409)
