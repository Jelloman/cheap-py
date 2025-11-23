"""Hashing utilities for CHEAP objects."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from cheap.core.aspect import Aspect
    from cheap.core.entity import Entity


class CheapHasher:
    """
    Utility class for generating consistent hashes of CHEAP objects.

    Uses SHA-256 for cryptographic hashing and provides methods for
    hashing entities, aspects, and other CHEAP data structures.
    """

    @staticmethod
    def hash_uuid(uuid: UUID) -> str:
        """
        Hash a UUID to a hexadecimal string.

        Args:
            uuid: The UUID to hash.

        Returns:
            Hexadecimal hash string (SHA-256).
        """
        return hashlib.sha256(uuid.bytes).hexdigest()

    @staticmethod
    def hash_string(value: str) -> str:
        """
        Hash a string to a hexadecimal string.

        Args:
            value: The string to hash.

        Returns:
            Hexadecimal hash string (SHA-256).
        """
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """
        Hash raw bytes to a hexadecimal string.

        Args:
            data: The bytes to hash.

        Returns:
            Hexadecimal hash string (SHA-256).
        """
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def hash_entity(cls, entity: Entity) -> str:
        """
        Generate a hash for an entity based on its ID.

        Args:
            entity: The entity to hash.

        Returns:
            Hexadecimal hash string (SHA-256) of the entity's ID.
        """
        return cls.hash_uuid(entity.id)

    @classmethod
    def hash_aspect(cls, aspect: Aspect) -> str:
        """
        Generate a hash for an aspect based on its definition's ID.

        Args:
            aspect: The aspect to hash.

        Returns:
            Hexadecimal hash string (SHA-256) of the aspect definition's ID.
        """
        return cls.hash_uuid(aspect.definition.id)

    @staticmethod
    def md5_hash_string(value: str) -> str:
        """
        Hash a string using MD5 (for compatibility, not security).

        Args:
            value: The string to hash.

        Returns:
            Hexadecimal hash string (MD5).

        Note:
            MD5 is not cryptographically secure. Use only for checksums.
        """
        return hashlib.md5(value.encode("utf-8")).hexdigest()

    @staticmethod
    def md5_hash_bytes(data: bytes) -> str:
        """
        Hash raw bytes using MD5 (for compatibility, not security).

        Args:
            data: The bytes to hash.

        Returns:
            Hexadecimal hash string (MD5).

        Note:
            MD5 is not cryptographically secure. Use only for checksums.
        """
        return hashlib.md5(data).hexdigest()
