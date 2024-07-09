import os


def get_env(key: str, raise_on_missing: bool = True) -> str:
    """Get the value of the given environment variable.

    Args:
        key: The name of the environment variable.
        raise_on_missing: Whether to raise an exception if the environment variable is missing.

    Raises:
        ValueError: If the environment variable is missing.

    Returns:
        str: The value of the environment variable.
    """
    value = os.environ.get(key, "")
    if not value and raise_on_missing:
        raise ValueError(f"Missing environment variable: {key}")

    return value
