import logging
import os

logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG_LOGGING", None) else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Args:
        name: The name of the logger.
    """
    return logging.getLogger(name)
