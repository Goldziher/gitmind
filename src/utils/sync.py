"""Async/sync utils module."""

from collections.abc import Callable
from functools import partial
from typing import ParamSpec, TypeVar, cast

from anyio.to_thread import run_sync as anyio_run_sync

P = ParamSpec("P")
T = TypeVar("T")


async def run_sync(fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Run a synchronous function in an asynchronous context.

    Notes:
        - we use partial to bind the function with the arguments and keyword arguments because run_until_complete
            expects a function with no arguments.

    Args:
        fn: The function to run.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The return value of the function.
    """
    bound_func = partial(fn, *args, **kwargs)
    return cast(T, (await anyio_run_sync(bound_func)))
