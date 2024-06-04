from abc import ABC, abstractmethod


class CacheBase(ABC):
    """ABC for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """Get a value from the cache.

        Args:
            key (str): The key to retrieve the value for.
        """
        raise NotImplementedError

    @abstractmethod
    async def set(
        self,
        key: str,
        value: str,
    ) -> None:
        """Set a value in the cache.

        Args:
            key: The key to store the value under.
            value: The value to store.

        Returns:
            None
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value from the cache.

        Args:
            key: The key to delete the value for.

        Returns:
            None
        """
        raise NotImplementedError

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.

        Args:
            key: The key to check the existence of.

        Returns:
            bool: True if the key exists, else False.
        """
        raise NotImplementedError
