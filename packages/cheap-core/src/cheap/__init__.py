"""Cheap Python - A data caching and metadata modeling system.

This is a namespace package that allows multiple cheap-* packages
to share the same 'cheap' namespace.
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)
