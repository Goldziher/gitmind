from unittest.mock import AsyncMock, Mock, patch

import pytest
from openai import OpenAIError
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.chat_completion_message_tool_call import Function

from gitmind.config import GitMindSettings
from gitmind.exceptions import EmptyContentError, LLMClientError
from gitmind.llm.base import MessageDefinition
from gitmind.llm.openai_client import OpenAIClient


@pytest.fixture()
def openai_config() -> GitMindSettings:
    return GitMindSettings(
        provider_api_key="fake_token",  # type: ignore[arg-type]
        provider_name="openai",
        provider_deployment_id="abc123jeronimo",
        provider_model="gpt-4o",
        target_repo="git@github.com:libgit2/pygit2.git",
    )


@pytest.fixture()
def azure_openai_config() -> GitMindSettings:
    return GitMindSettings(
        provider_endpoint_url="https://example.com/api",  # type: ignore[arg-type]
        provider_api_key="fake_token",  # type: ignore[arg-type]
        provider_name="azure-openai",
        provider_deployment_id="abc123jeronimo",
        provider_model="gpt-4o",
        target_repo="git@github.com:libgit2/pygit2.git",
    )


@pytest.fixture()
async def openai_client(openai_config: GitMindSettings) -> OpenAIClient:
    return OpenAIClient(
        api_key=openai_config.provider_api_key.get_secret_value(),
        model_name=openai_config.provider_model,
        endpoint_url=openai_config.provider_endpoint_url,  # type: ignore[arg-type]
    )


@pytest.fixture()
async def azure_client(azure_openai_config: GitMindSettings) -> OpenAIClient:
    return OpenAIClient(
        api_key=azure_openai_config.provider_api_key.get_secret_value(),
        model_name=azure_openai_config.provider_model,
        endpoint_url=azure_openai_config.provider_endpoint_url,  # type: ignore[arg-type]
        deployment_id=azure_openai_config.provider_deployment_id,
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
                                arguments='{"summary": "chore: add e2e testing", "purpose": "To integrate end-to-end (e2e) testing capabilities into the project.", "breakdown": [{"file_name": ".env", "changes_description": "Added a single line which appears to be a placeholder or default setting for the OpenAI API key."}, {"file_name": ".gitignore", "changes_description": "Included the .env file in the ignore list, likely to prevent sensitive data from being committed."}, {"file_name": "e2e/__init__.py", "changes_description": "An empty file was included, possibly as a placeholder to initialize the module."}, {"file_name": "e2e/describe_commit_test.py", "changes_description": "Added an end-to-end test script to test the describe_commit_contents function. This includes importing necessary modules, initializing an OpenAI client, retrieving commits, and generating descriptions."}, {"file_name": "pdm.lock", "changes_description": "Updated dependencies and hash values, reflecting changes in the package configurations."}, {"file_name": "pyproject.toml", "changes_description": "Updated configurations and removed any rules related to e2e testing."}, {"file_name": "src/commit.py", "changes_description": "Minor changes to imports and the handling of commit data extraction, updating to use a dictionary for file changes."}, {"file_name": "src/llm/base.py", "changes_description": "Modified the initialization method of the LLMClient class to be asynchronous."}, {"file_name": "src/llm/openai_client.py", "changes_description": "Refactored the OpenAIClient class by removing unnecessary imports and functions, updating methods for better readability and error handling."}, {"file_name": "src/llm/result.md", "changes_description": "Created a markdown file to describe commit results, potentially for documentation purposes."}, {"file_name": "src/prompts.py", "changes_description": "Adjusted imports to reflect new module structure."}, {"file_name": "src/repository.py", "changes_description": "Updated function definitions to be more clear, including parameter name changes for better readability."}, {"file_name": "src/types.py", "changes_description": "Refined the CommitDataDTO type definition by updating the type hints for better accuracy."}, {"file_name": "src/utils/serialization.py", "changes_description": "Updated the serialize function to use a sorted order for encoding."}], "programming_languages_used": ["Python", "TOML"], "additional_notes": "The commit focuses on integrating e2e testing and includes various updates to support this feature, impacting multiple files across the codebase."}',
                                name="describe_commit",
                            ),
                            type="function",
                        )
                    ],
                ),
            )
        ],
        created=1719340039,
        model="gpt-4o-2024-05-13",
        object="chat.completion",
        system_fingerprint="fp_66b29dffce",
        usage=CompletionUsage(completion_tokens=519, prompt_tokens=4355, total_tokens=4874),
    )


@patch("openai.AsyncClient", autospec=True)
async def test_init_openai_client(mock_client: Mock, openai_config: GitMindSettings) -> None:
    OpenAIClient(
        api_key=openai_config.provider_api_key.get_secret_value(),
        model_name=openai_config.provider_model,
        endpoint_url=openai_config.provider_endpoint_url,  # type: ignore[arg-type]
    )
    mock_client.assert_called_once()


@patch("openai.lib.azure.AsyncAzureOpenAI", autospec=True)
async def test_init_azure_client(mock_client: Mock, azure_openai_config: GitMindSettings) -> None:
    OpenAIClient(
        api_key=azure_openai_config.provider_api_key.get_secret_value(),
        model_name=azure_openai_config.provider_model,
        endpoint_url=azure_openai_config.provider_endpoint_url,  # type: ignore[arg-type]
        deployment_id=azure_openai_config.provider_deployment_id,
    )
    mock_client.assert_called_once()


async def test_create_completions_success(
    openai_client: OpenAIClient,
    describe_commit_message_definitions: list[MessageDefinition],
    describe_commit_chat_completion: ChatCompletion,
) -> None:
    openai_client._client.chat.completions.create = AsyncMock(return_value=describe_commit_chat_completion)  # type: ignore
    result = await openai_client.create_completions(messages=describe_commit_message_definitions, json_response=True)
    assert result == describe_commit_chat_completion.choices[0].message.tool_calls[0].function.arguments  # type: ignore


async def test_create_completions_empty_content(
    openai_client: OpenAIClient,
    describe_commit_message_definitions: list[MessageDefinition],
    describe_commit_chat_completion: ChatCompletion,
) -> None:
    describe_commit_chat_completion.choices[0].message.tool_calls[0].function.arguments = ""  # type: ignore
    openai_client._client.chat.completions.create = AsyncMock(return_value=describe_commit_chat_completion)  # type: ignore

    with pytest.raises(EmptyContentError):
        await openai_client.create_completions(messages=describe_commit_message_definitions, json_response=True)


async def test_create_completions_failure(
    openai_client: OpenAIClient, describe_commit_message_definitions: list[MessageDefinition]
) -> None:
    # Simulate an API error scenario
    openai_client._client.chat.completions.create = AsyncMock(side_effect=OpenAIError("API error"))  # type: ignore
    with pytest.raises(LLMClientError):
        await openai_client.create_completions(messages=describe_commit_message_definitions, json_response=True)
