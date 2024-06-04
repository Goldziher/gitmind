from hashlib import sha256


def get_sha_hash(content: str) -> str:
    """Get the SHA256 hash of the provided content.

    Args:
        content: The content to hash.

    Returns:
        str: The SHA256 hash of the content.
    """
    return sha256(content.encode()).hexdigest()
