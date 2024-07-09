from unittest.mock import AsyncMock, Mock, patch

import pytest
from groq import GroqError
from groq.types import CompletionUsage
from groq.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from groq.types.chat.chat_completion import ChatCompletion, Choice
from groq.types.chat.chat_completion_message_tool_call import Function
from tree_sitter_language_pack import SupportedLanguage

from git_critic.configuration_types import MessageDefinition
from git_critic.exceptions import EmptyContentError, LLMClientError
from git_critic.llm.groq_client import GroqClient, GroqOptions
from git_critic.utils.chunking import ChunkingType


@pytest.fixture
def groq_options() -> GroqOptions:
    return GroqOptions(api_key="fake_key")


@pytest.fixture
async def groq_client(groq_options: GroqOptions) -> GroqClient:
    return GroqClient(options=groq_options)


@pytest.fixture
def describe_commit_chat_completion() -> ChatCompletion:
    return ChatCompletion(
        id="chatcmpl-9e5AtvzgX3wpNKavzubGkSDSw67Ef",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                logprobs=None,
                message=ChatCompletionMessage(
                    content=None,
                    role="assistant",
                    function_call=None,
                    tool_calls=[
                        ChatCompletionMessageToolCall(
                            id="call_ufStr9emNldpwjQ4EJpJWuC0",
                            function=Function(
                                arguments='{"summary": "chore: add e2e testing", "purpose": "To integrate end-to-end (e2e) testing capabilities into the project.", "breakdown": [{"file_name": ".env", "changes_description": "Added a single line which appears to be a placeholder or default setting for the OpenAI API key."}, {"file_name": ".gitignore", "changes_description": "Included the .env file in the ignore list, likely to prevent sensitive data from being committed."}, {"file_name": "e2e/__init__.py", "changes_description": "An empty file was included, possibly as a placeholder to initialize the module."}, {"file_name": "e2e/test_describe_commit.py", "changes_description": "Added an end-to-end test script to test the describe_commit_contents function. This includes importing necessary modules, initializing an OpenAI client, retrieving commits, and generating descriptions."}, {"file_name": "pdm.lock", "changes_description": "Updated dependencies and hash values, reflecting changes in the package configurations."}, {"file_name": "pyproject.toml", "changes_description": "Updated configurations and removed any rules related to e2e testing."}, {"file_name": "src/commit.py", "changes_description": "Minor changes to imports and the handling of commit data extraction, updating to use a dictionary for file changes."}, {"file_name": "src/llm/base.py", "changes_description": "Modified the initialization method of the LLMClient class to be asynchronous."}, {"file_name": "src/llm/groq_client.py", "changes_description": "Refactored the GroqClient class by removing unnecessary imports and functions, updating methods for better readability and error handling."}, {"file_name": "src/llm/result.md", "changes_description": "Created a markdown file to describe commit results, potentially for documentation purposes."}, {"file_name": "src/prompts.py", "changes_description": "Adjusted imports to reflect new module structure."}, {"file_name": "src/repository.py", "changes_description": "Updated function definitions to be more clear, including parameter name changes for better readability."}, {"file_name": "src/types.py", "changes_description": "Refined the CommitDataDTO type definition by updating the type hints for better accuracy."}, {"file_name": "src/utils/serialization.py", "changes_description": "Updated the serialize function to use a sorted order for encoding."}], "programming_languages_used": ["Python", "TOML"], "additional_notes": "The commit focuses on integrating e2e testing and includes various updates to support this feature, impacting multiple files across the codebase."}',
                                name="describe_commit",
                            ),
                            type="function",
                        )
                    ],
                ),
            )
        ],
        created=1719340039,
        model="llama3-8b-8192-2024-05-13",
        object="chat.completion",
        system_fingerprint="fp_66b29dffce",
        usage=CompletionUsage(completion_tokens=519, prompt_tokens=4355, total_tokens=4874),
    )


@patch("groq.AsyncClient", autospec=True)
async def test_init_groq_client(mock_client: Mock, groq_options: GroqOptions) -> None:
    GroqClient(options=groq_options)
    mock_client.assert_called_once()


async def test_create_completions_success(
    groq_client: GroqClient,
    describe_commit_message_definitions: list[MessageDefinition],
    describe_commit_chat_completion: ChatCompletion,
) -> None:
    groq_client._client.chat.completions.create = AsyncMock(return_value=describe_commit_chat_completion)
    result = await groq_client.create_completions(messages=describe_commit_message_definitions, json_response=True)
    assert result == describe_commit_chat_completion.choices[0].message.tool_calls[0].function.arguments


async def test_create_completions_empty_content(
    groq_client: GroqClient,
    describe_commit_message_definitions: list[MessageDefinition],
    describe_commit_chat_completion: ChatCompletion,
) -> None:
    describe_commit_chat_completion.choices[0].message.tool_calls[0].function.arguments = ""
    groq_client._client.chat.completions.create = AsyncMock(return_value=describe_commit_chat_completion)

    with pytest.raises(EmptyContentError):
        await groq_client.create_completions(messages=describe_commit_message_definitions, json_response=True)


async def test_create_completions_failure(
    groq_client: GroqClient, describe_commit_message_definitions: list[MessageDefinition]
) -> None:
    # Simulate an API error scenario
    groq_client._client.chat.completions.create = AsyncMock(side_effect=GroqError("API error"))
    with pytest.raises(LLMClientError):
        await groq_client.create_completions(messages=describe_commit_message_definitions, json_response=True)


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
    groq_client: GroqClient,
    chunking_type: ChunkingType,
    content: str,
    expected_chunks: int,
    language: SupportedLanguage | None,
) -> None:
    content = "This is a test string to verify the chunk content functionality over the defined maximum token limit."
    max_tokens = 10
    chunks = list(groq_client.chunk_content(content, max_tokens, chunking_type, language))
    assert len(chunks) == expected_chunks
