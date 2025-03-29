text_mime_types = {"text", "application/json", "application/xml", "application/javascript"}


def is_supported_mime_type(mime_type: str) -> bool:
    """Check if a MIME type is supported for parsing.

    Args:
        mime_type: The MIME type to check.

    Returns:
        True if the MIME type is supported, False otherwise.
    """
    return any(mime_type.startswith(mime_type_prefix) for mime_type_prefix in text_mime_types)
