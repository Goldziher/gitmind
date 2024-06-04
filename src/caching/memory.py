from __future__ import annotations

from anyio import Lock

from src.caching.base import CacheBase


class InMemoryCache(CacheBase):
    """In-memory cache implementation."""

    _store: dict[str, str]
    _lock: Lock

    def __init__(self) -> None:
        """Initialize the in-memory cache."""
        super().__init__()
        self._store: dict[str, str] = {}
        self._lock = Lock()

    async def set(self, key: str, value: str) -> None:
        """Set a value.

        Args:
            key: The key to associate with the value
            value: The value to store

        Returns:
            None
        """
        async with self._lock:
            self._store[key] = value

    async def get(self, key: str) -> str | None:
        """Get a value.

        Args:
            key: Key associated with the value

        Returns:
            The cached value or None if the key does not exist
        """
        async with self._lock:
            return self._store.get(key)

    async def delete(self, key: str) -> None:
        """Delete a value.

        Args:
            key: The key to delete the value for

        Returns:
            None
        """
        async with self._lock:
            self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.

        Args:
            key: The key to check the existence of.

        Returns:
            bool: True if the key exists, else False.
        """
        return key in self._store
