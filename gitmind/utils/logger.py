import logging
from sys import stdout
from typing import cast

from structlog.typing import FilteringBoundLogger

from gitmind.utils.env import get_env
from gitmind.utils.ref import Ref
from gitmind.utils.serialization import serialize

configured_ref = Ref[bool]()


def get_logger(name: str) -> FilteringBoundLogger:
    """Get a logger with the given name.

    Args:
        name: The name of the logger.
    """
    if configured_ref.value is None:
        from structlog import BytesLoggerFactory, PrintLoggerFactory, configure_once, make_filtering_bound_logger
        from structlog.contextvars import merge_contextvars
        from structlog.dev import ConsoleRenderer
        from structlog.processors import JSONRenderer, TimeStamper, add_log_level, format_exc_info

        configure_once(  # will raise an error if called more than once
            cache_logger_on_first_use=True,
            wrapper_class=make_filtering_bound_logger(
                logging.DEBUG if get_env("DEBUG", raise_on_missing=False) else logging.INFO
            ),
            processors=[
                merge_contextvars,
                add_log_level,
                format_exc_info,
                TimeStamper(fmt="iso", utc=True),
                ConsoleRenderer(colors=True) if stdout.isatty() else JSONRenderer(serializer=serialize),  # type: ignore[list-item]
            ],
            logger_factory=PrintLoggerFactory() if stdout.isatty() else BytesLoggerFactory(),
        )

        configured_ref.value = True

    from structlog import get_logger as get_structlog_logger

    return cast(FilteringBoundLogger, get_structlog_logger(name))
