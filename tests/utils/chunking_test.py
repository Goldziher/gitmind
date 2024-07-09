import pytest
from semantic_text_splitter import CodeSplitter, MarkdownSplitter, TextSplitter

from git_critic.utils.chunking import ChunkingType, get_chunker


@pytest.mark.parametrize(
    "chunking_type, expected_cls", (("text", TextSplitter), ("markdown", MarkdownSplitter), ("code", CodeSplitter))
)
def test_get_chunker(chunking_type: ChunkingType, expected_cls: type) -> None:
    assert get_chunker(chunking_type) is expected_cls
