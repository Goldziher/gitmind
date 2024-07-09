from collections.abc import Generator
from pathlib import Path as SyncPath

import pytest
from anyio import Path as AsyncPath
from anyio import create_task_group

from gitmind.caching.file import DEFAULT_FOLDER_NAME, FileSystemCache, get_or_create_cache_dir


@pytest.fixture
async def file_system_cache(tmp_path: SyncPath) -> FileSystemCache:
    tmp_path = tmp_path / DEFAULT_FOLDER_NAME
    return FileSystemCache(cache_dir=tmp_path)


@pytest.fixture
def existing_cache_dir() -> Generator[SyncPath, None, None]:
    cache_dir = SyncPath.cwd() / ".existing_cache_dir"
    cache_dir.mkdir(exist_ok=True)
    yield cache_dir
    cache_dir.rmdir()


@pytest.fixture
def non_existing_cache_dir() -> Generator[SyncPath, None, None]:
    cache_dir = SyncPath.cwd() / ".non_existing_cache_dir"
    yield cache_dir
    if cache_dir.exists():
        cache_dir.rmdir()


@pytest.fixture
def default_cache_dir() -> Generator[SyncPath, None, None]:
    cache_dir = SyncPath.cwd() / DEFAULT_FOLDER_NAME
    yield cache_dir
    if cache_dir.exists():
        cache_dir.rmdir()


async def test_file_system_cache_set_get(file_system_cache: FileSystemCache) -> None:
    await file_system_cache.set("test_key", "test_value")
    assert await file_system_cache.get("test_key") == "test_value"


@pytest.mark.asyncio
async def test_file_system_cache_set_with_bytes(file_system_cache: FileSystemCache) -> None:
    await file_system_cache.set("binary_key", b"binary_value")
    assert await file_system_cache.get("binary_key") == "binary_value"


@pytest.mark.asyncio
async def test_file_system_cache_non_existent_get(file_system_cache: FileSystemCache) -> None:
    assert await file_system_cache.get("non_existent_key") is None


@pytest.mark.asyncio
async def test_file_system_cache_delete(file_system_cache: FileSystemCache) -> None:
    await file_system_cache.set("test_key", "test_value")
    await file_system_cache.delete("test_key")
    assert await file_system_cache.get("test_key") is None


@pytest.mark.asyncio
async def test_file_system_cache_delete_non_existent(file_system_cache: FileSystemCache) -> None:
    # Ensure no exception is raised
    await file_system_cache.delete("non_existent_key")
    assert not await file_system_cache.exists("non_existent_key")


@pytest.mark.asyncio
async def test_file_system_cache_exists(file_system_cache: FileSystemCache) -> None:
    await file_system_cache.set("test_key", "test_value")
    assert await file_system_cache.exists("test_key") is True
    await file_system_cache.delete("test_key")
    assert await file_system_cache.exists("test_key") is False


@pytest.mark.asyncio
async def test_file_system_cache_concurrent_access(file_system_cache: FileSystemCache) -> None:
    async with create_task_group() as tg:
        tg.start_soon(file_system_cache.set, "key1", "value1")
        tg.start_soon(file_system_cache.set, "key2", "value2")
        tg.start_soon(file_system_cache.delete, "key1")
        assert await file_system_cache.exists("key1") is False
        assert await file_system_cache.get("key2") == "value2"


def test_get_or_create_cache_dir_with_existing_cache_dir(existing_cache_dir: SyncPath) -> None:
    assert get_or_create_cache_dir(existing_cache_dir) == AsyncPath(existing_cache_dir)


def test_get_or_create_cache_dir_with_non_existing_cache_dir(non_existing_cache_dir: SyncPath) -> None:
    assert get_or_create_cache_dir(non_existing_cache_dir) == AsyncPath(non_existing_cache_dir)
    assert non_existing_cache_dir.exists()


def test_get_or_create_cache_dir_with_none(default_cache_dir: SyncPath) -> None:
    path = get_or_create_cache_dir(None)
    assert path == default_cache_dir
    assert path.exists()


def test_is_idempotent() -> None:
    path = get_or_create_cache_dir(None)
    assert path == get_or_create_cache_dir(None)
