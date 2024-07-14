"""Async/sync utils module."""

from asyncio import run as run_async
from collections.abc import Awaitable, Callable, Coroutine
from functools import partial, wraps
from typing import Any, ParamSpec, TypeVar, cast

from anyio.to_thread import run_sync as anyio_run_sync

P = ParamSpec("P")
T = TypeVar("T")
C = TypeVar("C", bound=Awaitable[Any] | Coroutine[None, None, Any])


async def run_sync(fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Run a synchronous function in an asynchronous context.

    Notes:
        - we use partial to bind the function with the arguments and keyword arguments because anyio.run_sync
            cannot handle kwargs.

    Args:
        fn: The function to run.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The return value of the function.
    """
    bound_func = partial(fn, *args, **kwargs)
    return cast(T, (await anyio_run_sync(bound_func)))


def run_as_sync(async_fn: Callable[P, Coroutine[None, None, T]]) -> Callable[P, T]:
    """Decorator to run an async function in a synchronous context.

    Returns:
        A wrapped function that runs the async function in a synchronous context.
    """

    @wraps(async_fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return run_async(async_fn(*args, **kwargs))

    return wrapper
