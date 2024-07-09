import pytest

from gitmind.utils.sync import run_sync


def no_args() -> str:
    return "no_args"


def with_args(a: int, b: int) -> int:
    return a + b


def with_kwargs(*, key: str) -> str:
    return key


def raises_exception() -> None:
    raise ValueError("Error")


async def test_running_sync_function_without_arguments_returns_expected_result() -> None:
    result = await run_sync(no_args)
    assert result == "no_args"


async def test_running_sync_function_with_arguments_returns_expected_result() -> None:
    result = await run_sync(with_args, 1, 2)
    assert result == 3


async def test_running_sync_function_with_keyword_arguments_returns_expected_result() -> None:
    result = await run_sync(with_kwargs, key="value")
    assert result == "value"


async def test_running_sync_function_that_raises_exception_propagates_exception() -> None:
    with pytest.raises(ValueError) as exc_info:
        await run_sync(raises_exception)
    assert str(exc_info.value) == "Error"
