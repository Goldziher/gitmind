import pytest
from anyio import create_task_group

from git_critic.caching import InMemoryCache


@pytest.fixture
async def in_memory_cache() -> InMemoryCache:
    return InMemoryCache()


async def test_set_and_get_value(in_memory_cache: InMemoryCache) -> None:
    await in_memory_cache.set("key1", "value1")
    assert await in_memory_cache.get("key1") == "value1", "Should retrieve the value correctly."


async def test_get_nonexistent_key(in_memory_cache: InMemoryCache) -> None:
    assert await in_memory_cache.get("nonexistent") is None, "Should return None for a nonexistent key."


async def test_delete_key(in_memory_cache: InMemoryCache) -> None:
    await in_memory_cache.set("key2", "value2")
    await in_memory_cache.delete("key2")
    assert await in_memory_cache.get("key2") is None, "Should return None after the key is deleted."


async def test_exists_key(in_memory_cache: InMemoryCache) -> None:
    await in_memory_cache.set("key3", "value3")
    assert await in_memory_cache.exists("key3") is True, "Key should exist in the cache."
    await in_memory_cache.delete("key3")
    assert not await in_memory_cache.exists("key3"), "Key should no longer exist after deletion."


async def test_concurrent_access(in_memory_cache: InMemoryCache) -> None:
    async with create_task_group() as tg:
        tg.start_soon(in_memory_cache.set, "key1", "value1")
        tg.start_soon(in_memory_cache.set, "key2", "value2")
        tg.start_soon(in_memory_cache.delete, "key1")
    assert await in_memory_cache.get("key1") is None, "Key1 should be deleted."
    assert await in_memory_cache.get("key2") == "value2", "Key2 should have the correct value."


async def test_overwrite_existing_key(in_memory_cache: InMemoryCache) -> None:
    await in_memory_cache.set("key4", "initial")
    await in_memory_cache.set("key4", "updated")
    assert await in_memory_cache.get("key4") == "updated", "Key should hold the updated value."
