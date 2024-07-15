from unittest.mock import AsyncMock, Mock, patch

import pytest
from groq import GroqError
from groq.types import CompletionUsage
from groq.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from groq.types.chat.chat_completion import ChatCompletion, Choice
from groq.types.chat.chat_completion_message_tool_call import Function

from gitmind.config import GitMindSettings
from gitmind.exceptions import EmptyContentError, LLMClientError
from gitmind.llm.base import MessageDefinition
from gitmind.llm.groq_client import GroqClient


@pytest.fixture()
def groq_config() -> GitMindSettings:
    return GitMindSettings(
        provider_api_key="fake_token",  # type: ignore[arg-type]
        provider_name="groq",
        provider_model="llama3-70b-8192",
        target_repo="git@github.com:libgit2/pygit2.git",
    )


@pytest.fixture()
async def groq_client(groq_config: GitMindSettings) -> GroqClient:
    return GroqClient(
        api_key=groq_config.provider_api_key.get_secret_value(),
        model_name=groq_config.provider_model,
        endpoint_url=groq_config.provider_endpoint_url,  # type: ignore[arg-type]
    )


@pytest.fixture()
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
                                arguments='{"summary": "chore: add e2e testing", "purpose": "To integrate end-to-end (e2e) testing capabilities into the project.", "breakdown": [{"file_name": ".env", "changes_description": "Added a single line which appears to be a placeholder or default setting for the OpenAI API key."}, {"file_name": ".gitignore", "changes_description": "Included the .env file in the ignore list, likely to prevent sensitive data from being committed."}, {"file_name": "e2e/__init__.py", "changes_description": "An empty file was included, possibly as a placeholder to initialize the module."}, {"file_name": "e2e/describe_commit_test.py", "changes_description": "Added an end-to-end test script to test the describe_commit_contents function. This includes importing necessary modules, initializing an OpenAI client, retrieving commits, and generating descriptions."}, {"file_name": "pdm.lock", "changes_description": "Updated dependencies and hash values, reflecting changes in the package configurations."}, {"file_name": "pyproject.toml", "changes_description": "Updated configurations and removed any rules related to e2e testing."}, {"file_name": "src/commit.py", "changes_description": "Minor changes to imports and the handling of commit data extraction, updating to use a dictionary for file changes."}, {"file_name": "src/llm/base.py", "changes_description": "Modified the initialization method of the LLMClient class to be asynchronous."}, {"file_name": "src/llm/groq_client.py", "changes_description": "Refactored the GroqClient class by removing unnecessary imports and functions, updating methods for better readability and error handling."}, {"file_name": "src/llm/result.md", "changes_description": "Created a markdown file to describe commit results, potentially for documentation purposes."}, {"file_name": "src/prompts.py", "changes_description": "Adjusted imports to reflect new module structure."}, {"file_name": "src/repository.py", "changes_description": "Updated function definitions to be more clear, including parameter name changes for better readability."}, {"file_name": "src/types.py", "changes_description": "Refined the CommitDataDTO type definition by updating the type hints for better accuracy."}, {"file_name": "src/utils/serialization.py", "changes_description": "Updated the serialize function to use a sorted order for encoding."}], "programming_languages_used": ["Python", "TOML"], "additional_notes": "The commit focuses on integrating e2e testing and includes various updates to support this feature, impacting multiple files across the codebase."}',
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
async def test_init_groq_client(mock_client: Mock, groq_config: GitMindSettings) -> None:
    GroqClient(
        api_key=groq_config.provider_api_key.get_secret_value(),
        model_name=groq_config.provider_model,
        endpoint_url=groq_config.provider_endpoint_url,  # type: ignore[arg-type]
    )
    mock_client.assert_called_once()


async def test_create_completions_success(
    groq_client: GroqClient,
    describe_commit_message_definitions: list[MessageDefinition],
    describe_commit_chat_completion: ChatCompletion,
) -> None:
    groq_client._client.chat.completions.create = AsyncMock(return_value=describe_commit_chat_completion)
    result = await groq_client.create_completions(messages=describe_commit_message_definitions, json_response=True)
    assert result == describe_commit_chat_completion.choices[0].message.tool_calls[0].function.arguments  # type: ignore


async def test_create_completions_empty_content(
    groq_client: GroqClient,
    describe_commit_message_definitions: list[MessageDefinition],
    describe_commit_chat_completion: ChatCompletion,
) -> None:
    describe_commit_chat_completion.choices[0].message.tool_calls[0].function.arguments = ""  # type: ignore
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
