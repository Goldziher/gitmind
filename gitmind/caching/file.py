from __future__ import annotations

from pathlib import Path as SyncPath
from pathlib import PurePath
from typing import TYPE_CHECKING, Final

from anyio import Path as AsyncPath

from gitmind.caching.base import CacheBase

if TYPE_CHECKING:
    from os import PathLike

DEFAULT_FOLDER_NAME: Final[str] = ".gitmind"


def get_or_create_cache_dir(cache_dir: str | PathLike[str] | SyncPath | None = None) -> AsyncPath:
    """Get or create the cache directory.

    Notes:
        - This function is synchronous because it is only called once at startup.

    Args:
        cache_dir: The name of the cache directory.

    Returns:
        Path: The path to the cache directory.
    """
    dir_path = SyncPath(cache_dir).resolve() if cache_dir else SyncPath.cwd().resolve() / DEFAULT_FOLDER_NAME
    dir_path.mkdir(exist_ok=True)

    return AsyncPath(dir_path)


class FileSystemCache(CacheBase):
    """File system cache implementation.

    Args:
        cache_dir: The name of the cache directory.
    """

    _cache_dir: AsyncPath

    def __init__(self, cache_dir: str | PathLike[str] | PurePath | None = None) -> None:
        super().__init__()
        self._cache_dir = get_or_create_cache_dir(cache_dir=cache_dir)

    async def get(self, key: str) -> str | None:
        """Get a value from the cache.

        Args:
            key: The key to retrieve the value for.

        Returns:
            The cached value or None if the key does not exist.
        """
        cache_file = self._cache_dir / key
        try:
            return await cache_file.read_text()
        except FileNotFoundError:
            return None

    async def set(self, key: str, value: str | bytes) -> None:
        """Set a value in the cache.

        Args:
            key: The key to store the value under.
            value: The value to store.

        Returns:
            None
        """
        cache_file = self._cache_dir / key
        await cache_file.write_text(value if not isinstance(value, bytes) else value.decode())

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
            True if the key exists, else False.
        """
        cache_file = self._cache_dir / key
        return await cache_file.exists()
