from collections.abc import Generator
from typing import Literal, overload

from semantic_text_splitter import CodeSplitter, MarkdownSplitter, TextSplitter
from tree_sitter_language_pack import SupportedLanguage, get_binding

TextualChunkingType = Literal["text", "markdown"]
CodeChunkingType = Literal["code"]

ChunkingType = TextualChunkingType | CodeChunkingType


@overload
def get_chunker(
    *, chunk_size: int, chunking_type: TextualChunkingType, model: str, language: None = None
) -> TextSplitter | MarkdownSplitter: ...


@overload
def get_chunker(
    *, chunk_size: int, chunking_type: CodeChunkingType, model: str, language: SupportedLanguage
) -> CodeSplitter: ...


def get_chunker(
    *,
    chunk_size: int,
    chunking_type: ChunkingType,
    model: str,
    language: SupportedLanguage | None = None,
) -> TextSplitter | MarkdownSplitter | CodeSplitter:
    """Get the chunker for the given chunking type.

    Args:
        chunk_size: The maximal number of tokens per chunk.
        chunking_type: The type of content to chunk.
        model: The model name, e.g. gpt-3.5-turbo.
        language: The coding language to chunk - if the content is code.

    Raises:
        ValueError: If the language is not provided for code chunking.

    Returns:
        The chunker for the given chunking type.
    """
    if chunking_type == "code":
        if not language:
            raise ValueError("Language is required for code chunking")

        return CodeSplitter.from_tiktoken_model(model=model, capacity=chunk_size, language=get_binding(language))

    if chunking_type == "markdown":
        return MarkdownSplitter.from_tiktoken_model(model=model, capacity=chunk_size)

    return TextSplitter.from_tiktoken_model(model=model, capacity=chunk_size)


@overload
def chunk_content(
    content: str, *, chunk_size: int, chunking_type: TextualChunkingType, model: str
) -> Generator[str, None, None]: ...


@overload
def chunk_content(
    content: str, *, chunk_size: int, chunking_type: CodeChunkingType, model: str, language: SupportedLanguage
) -> Generator[str, None, None]: ...


def chunk_content(
    content: str,
    *,
    chunk_size: int,
    chunking_type: ChunkingType,
    model: str,
    language: SupportedLanguage | None = None,
) -> Generator[str, None, None]:
    """Chunk the given content into chunks of the given size.

    Args:
        chunk_size: The maximal number of tokens per chunk.
        chunking_type: The type of content to chunk.
        content: The content to chunk.
        model: The model name, e.g. gpt-3.5-turbo.
        language: The coding language to chunk - if the content is code.

    Raises:
        ValueError: If the language is not provided for code chunking.

    Yields:
        The chunks of the content.
    """
    chunker = get_chunker(chunking_type=chunking_type, model=model, chunk_size=chunk_size, language=language)  # type: ignore[arg-type]

    yield from chunker.chunks(content)
