from pathlib import Path as SyncPath

from anyio import Path as AsyncPath

from src.caching.base import CacheBase


def get_or_create_cache_dir() -> AsyncPath:
    """Get or create the cache directory.

    Notes:
        - This function is synchronous because it is only called once at startup.

    Returns:
        Path: The path to the cache directory.
    """
    cwd = SyncPath(__file__).parent.resolve()
    cache_dir = cwd / ".critic"
    cache_dir.mkdir(exist_ok=True)

    return AsyncPath(cache_dir)


class FileSystemCache(CacheBase):
    """File system cache implementation."""

    _cache_dir: AsyncPath

    def __init__(self) -> None:
        """Initialize the file system cache."""
        super().__init__()
        self._cache_dir = get_or_create_cache_dir()

    async def get(self, key: str) -> str | None:
        """Get a value from the cache.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            str | None: The cached value or None if the key does not exist.
        """
        cache_file = self._cache_dir / key
        try:
            return await cache_file.read_text()
        except FileNotFoundError:
            return None

    async def set(self, key: str, value: str) -> None:
        """Set a value in the cache.

        Args:
            key: The key to store the value under.
            value: The value to store.

        Returns:
            None
        """
        cache_file = self._cache_dir / key
        await cache_file.write_text(value)

    async def delete(self, key: str) -> None:
        """Delete a value from the cache.

        Args:
            key: The key to delete the value for.

        Returns:
            None
        """
        cache_file = self._cache_dir / key
        await cache_file.unlink(missing_ok=True)

    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.

        Args:
            key: The key to check the existence of.

        Returns:
            bool: True if the key exists, else False.
        """
        cache_file = self._cache_dir / key
        return await cache_file.exists()
