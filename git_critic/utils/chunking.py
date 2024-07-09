from typing import Literal

from semantic_text_splitter import CodeSplitter, MarkdownSplitter, TextSplitter

ChunkingType = Literal["text", "markdown", "code"]


def get_chunker(chunking_type: ChunkingType) -> type[TextSplitter] | type[MarkdownSplitter] | type[CodeSplitter]:
    """Get the chunker for the given chunking type.

    Args:
        chunking_type: The type of content to chunk.

    Returns:
        The chunker for the given chunking type.
    """
    if chunking_type == "text":
        return TextSplitter
    if chunking_type == "markdown":
        return MarkdownSplitter
    return CodeSplitter
