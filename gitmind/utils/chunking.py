from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from semantic_text_splitter import CodeSplitter, MarkdownSplitter, TextSplitter
from tree_sitter_language_pack import SupportedLanguage, get_binding
from typing_extensions import TypeAlias

if TYPE_CHECKING:
    from collections.abc import Generator

TextualChunkingType = Literal["text", "markdown"]
CodeChunkingType = Literal["code"]

ChunkingType: TypeAlias = "TextualChunkingType | CodeChunkingType"


@overload
def get_chunker(
    *,
    chunk_size: int,
    chunking_type: TextualChunkingType,
    language: None = None,
    model: str,
) -> TextSplitter | MarkdownSplitter: ...


@overload
def get_chunker(
    *,
    chunk_size: int,
    chunking_type: CodeChunkingType,
    language: SupportedLanguage,
    model: str,
) -> CodeSplitter: ...


def get_chunker(
    *,
    chunk_size: int,
    chunking_type: ChunkingType,
    language: SupportedLanguage | None = None,
    model: str,
) -> TextSplitter | MarkdownSplitter | CodeSplitter:
    """Get the chunker for the given chunking type.

    Args:
        chunk_size: The maximal number of tokens per chunk.
        chunking_type: The type of content to chunk.
        language: The coding language to chunk - if the content is code.
        model: The model name, e.g. gpt-3.5-turbo.

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
    content: str,
    *,
    chunk_size: int,
    chunking_type: CodeChunkingType,
    language: SupportedLanguage,
    model: str,
) -> Generator[str, None, None]: ...


def chunk_content(
    content: str,
    *,
    chunk_size: int,
    chunking_type: ChunkingType,
    language: SupportedLanguage | None = None,
    model: str,
) -> Generator[str, None, None]:
    """Chunk the given content into chunks of the given size.

    Args:
        content: The content to chunk.
        chunk_size: The maximal number of tokens per chunk.
        chunking_type: The type of content to chunk.
        language: The coding language to chunk - if the content is code.
        model: The model name, e.g. gpt-3.5-turbo.

    Yields:
        str: A chunk string
    """
    chunker = get_chunker(chunking_type=chunking_type, model=model, chunk_size=chunk_size, language=language)  # type: ignore[arg-type]
    yield from chunker.chunks(content)
