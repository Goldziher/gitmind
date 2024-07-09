import pytest
from semantic_text_splitter import CodeSplitter, MarkdownSplitter, TextSplitter
from tree_sitter_language_pack import SupportedLanguage

from gitmind.utils.chunking import ChunkingType, chunk_content, get_chunker


@pytest.mark.parametrize(
    "chunking_type, expected_cls, language",
    (
        ("text", TextSplitter, None),
        ("markdown", MarkdownSplitter, None),
        ("code", CodeSplitter, "python"),
    ),
)
def test_get_chunker(chunking_type: ChunkingType, expected_cls: type, language: SupportedLanguage | None) -> None:
    assert isinstance(
        get_chunker(chunking_type=chunking_type, chunk_size=10, model="gpt-3.5-turbo", language=language),  # type: ignore[arg-type]
        expected_cls,
    )


def test_get_code_chunker_wihtout_language_raises() -> None:
    with pytest.raises(ValueError):
        get_chunker(chunking_type="code", chunk_size=10, model="gpt-3.5-turbo", language=None)  # type: ignore[call-overload]


@pytest.mark.parametrize(
    "chunking_type, content, expected_chunks, language",
    (
        (
            "text",
            """
                            Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin
                            literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney
                            College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage,
                            and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum
                            comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by
                            Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance.
                            The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section
                            """,
            2,
            None,
        ),
        (
            "markdown",
            """
                            # Lorem Ipsum Intro

                            Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature
                            from 45 BC, making it over 2000 years old.

                            Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin
                            words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature,
                            discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum"
                            (The Extremes of Good and Evil) by Cicero, written in 45 BC.
                            This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum,
                            "Lorem ipsum dolor sit amet..", comes from a line in section.
                            """,
            2,
            None,
        ),
        (
            "code",
            """
                     import kotlin.random.Random

                     fun main() {
                         val randomNumbers = IntArray(10) { Random.nextInt(1, 100) } // Generate an array of 10 random integers between 1 and 99
                         println("Random numbers:")
                         for (number in randomNumbers) {
                             println(number)  // Print each random number
                         }
                     }
                     """,
            2,
            "kotlin",
        ),
    ),
)
async def test_chunk_content(
    chunking_type: ChunkingType,
    content: str,
    expected_chunks: int,
    language: SupportedLanguage | None,
) -> None:
    content = "This is a test string to verify the chunk content functionality over the defined maximum token limit."
    chunks = list(
        chunk_content(
            content=content,
            model="gpt-3.5-turbo",
            chunking_type=chunking_type,  # type: ignore[arg-type]
            chunk_size=10,
            language=language,  # type: ignore[arg-type]
        )
    )
    assert len(chunks) == expected_chunks
