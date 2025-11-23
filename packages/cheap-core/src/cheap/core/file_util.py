"""File utilities for CHEAP data persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Final


class CheapFileUtil:
    """
    Utility class for file operations in the CHEAP system.

    Provides convenient methods for working with files and directories
    using Python's pathlib.Path API.
    """

    # Common file extensions
    JSON_EXT: Final[str] = ".json"
    DB_EXT: Final[str] = ".db"
    SQLITE_EXT: Final[str] = ".sqlite"

    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            path: Path to the directory.

        Returns:
            The path to the directory.

        Raises:
            OSError: If the directory cannot be created.
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def ensure_parent_directory(file_path: Path) -> Path:
        """
        Ensure the parent directory of a file exists.

        Args:
            file_path: Path to a file.

        Returns:
            The path to the parent directory.

        Raises:
            OSError: If the directory cannot be created.
        """
        parent = file_path.parent
        parent.mkdir(parents=True, exist_ok=True)
        return parent

    @staticmethod
    def read_text(path: Path, encoding: str = "utf-8") -> str:
        """
        Read text from a file.

        Args:
            path: Path to the file.
            encoding: Text encoding (default: utf-8).

        Returns:
            File contents as a string.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            IOError: If the file cannot be read.
        """
        return path.read_text(encoding=encoding)

    @staticmethod
    def write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
        """
        Write text to a file.

        Args:
            path: Path to the file.
            content: Text content to write.
            encoding: Text encoding (default: utf-8).

        Raises:
            OSError: If the file cannot be written.
        """
        CheapFileUtil.ensure_parent_directory(path)
        path.write_text(content, encoding=encoding)

    @staticmethod
    def read_bytes(path: Path) -> bytes:
        """
        Read binary data from a file.

        Args:
            path: Path to the file.

        Returns:
            File contents as bytes.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            IOError: If the file cannot be read.
        """
        return path.read_bytes()

    @staticmethod
    def write_bytes(path: Path, data: bytes) -> None:
        """
        Write binary data to a file.

        Args:
            path: Path to the file.
            data: Binary data to write.

        Raises:
            OSError: If the file cannot be written.
        """
        CheapFileUtil.ensure_parent_directory(path)
        path.write_bytes(data)

    @staticmethod
    def delete_file(path: Path, missing_ok: bool = True) -> bool:
        """
        Delete a file.

        Args:
            path: Path to the file.
            missing_ok: If True, don't raise an error if file doesn't exist.

        Returns:
            True if file was deleted, False if it didn't exist.

        Raises:
            OSError: If the file cannot be deleted and missing_ok is False.
        """
        try:
            path.unlink()
            return True
        except FileNotFoundError:
            if not missing_ok:
                raise
            return False

    @staticmethod
    def delete_directory(path: Path, missing_ok: bool = True) -> bool:
        """
        Delete a directory and all its contents.

        Args:
            path: Path to the directory.
            missing_ok: If True, don't raise an error if directory doesn't exist.

        Returns:
            True if directory was deleted, False if it didn't exist.

        Raises:
            OSError: If the directory cannot be deleted and missing_ok is False.
        """
        if not path.exists():
            if not missing_ok:
                raise FileNotFoundError(f"Directory not found: {path}")
            return False

        # Delete all files and subdirectories
        for item in path.rglob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()

        # Delete the directory itself
        path.rmdir()
        return True

    @staticmethod
    def file_exists(path: Path) -> bool:
        """
        Check if a file exists.

        Args:
            path: Path to check.

        Returns:
            True if the file exists and is a file, False otherwise.
        """
        return path.is_file()

    @staticmethod
    def directory_exists(path: Path) -> bool:
        """
        Check if a directory exists.

        Args:
            path: Path to check.

        Returns:
            True if the directory exists and is a directory, False otherwise.
        """
        return path.is_dir()

    @staticmethod
    def get_file_size(path: Path) -> int:
        """
        Get the size of a file in bytes.

        Args:
            path: Path to the file.

        Returns:
            File size in bytes.

        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        return path.stat().st_size

    @staticmethod
    def list_files(directory: Path, pattern: str = "*") -> list[Path]:
        """
        List all files in a directory matching a pattern.

        Args:
            directory: Directory to search.
            pattern: Glob pattern to match (default: "*" for all files).

        Returns:
            List of file paths.

        Raises:
            FileNotFoundError: If the directory doesn't exist.
        """
        return sorted([p for p in directory.glob(pattern) if p.is_file()])

    @staticmethod
    def list_directories(directory: Path, pattern: str = "*") -> list[Path]:
        """
        List all subdirectories in a directory matching a pattern.

        Args:
            directory: Directory to search.
            pattern: Glob pattern to match (default: "*" for all directories).

        Returns:
            List of directory paths.

        Raises:
            FileNotFoundError: If the directory doesn't exist.
        """
        return sorted([p for p in directory.glob(pattern) if p.is_dir()])
