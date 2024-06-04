"""Serialization related utils."""

from typing import Any

from msgspec.json import decode, encode


def deserialize[T](value: str | bytes, target_type: type[T]) -> T:
    """Decode a JSON string/bytes into an object.

    Args:
        value: Value to decode.
        target_type: A type to decode the data into.

    Returns:
        An instance of ``target_type``.

    Raises:
        DecodeError: If error decoding ``value``.
    """
    return decode(value, type=target_type)


def serialize(value: Any) -> bytes:
    """Encode an object into a JSON string.

    Args:
        value: Value to serialize to JSON.

    Returns:
        A JSON string.

    Raises:
        EncodeError: If error encoding ``value``.
    """
    return encode(value, order="sorted")
