"""Serialization related utils."""

from enum import Enum
from inspect import isclass
from typing import Any, TypeVar

from msgspec.json import decode, encode
from pydantic import BaseModel

T = TypeVar("T")


def decode_hook(target: Any, value: dict) -> Any:
    """Decode a dictionary into an object.

    Args:
        target: The type to decode the data into.
        value: The dictionary to decode.

    Returns:
        An instance of ``type_``.
    """
    if isclass(target) and issubclass(target, BaseModel):
        return target(**value)

    raise TypeError(f"Unsupported type: {type(target)!r}")


def encode_hook(obj: Any) -> dict:
    """Encode an object into a dictionary.

    Args:
        obj: The object to encode.

    Returns:
        A dictionary representation of ``obj``.
    """
    if isinstance(obj, BaseModel):
        return {k: v if not isinstance(v, Enum) else v.value for (k, v) in obj.model_dump().items()}

    raise TypeError(f"Unsupported type: {type(obj)!r}")


def deserialize(value: str | bytes, target_type: type[T]) -> T:
    """Decode a JSON string/bytes into an object.

    Args:
        value: Value to decode.
        target_type: A type to decode the data into.

    Returns:
        An instance of ``target_type``.
    """
    return decode(value, type=target_type, dec_hook=decode_hook)


def serialize(value: Any) -> bytes:
    """Encode an object into a JSON string.

    Args:
        value: Value to serialize to JSON.

    Returns:
        A JSON string.
    """
    return encode(value, order="sorted", enc_hook=encode_hook)
