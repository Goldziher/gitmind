import pytest

from src.commit import is_supported_mime_type


@pytest.mark.parametrize(
    "mime_type, expected",
    (
        ("text/plain", True),
        ("text/html", True),
        ("application/json", True),
        ("application/xml", True),
        ("image/png", False),
        ("image/jpeg", False),
    ),
)
def test_is_supported_mime_type(mime_type: str, expected: str) -> None:
    assert is_supported_mime_type(mime_type) == expected
