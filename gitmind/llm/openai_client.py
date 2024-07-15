from typing import TYPE_CHECKING, Any, Union, cast

from gitmind.exceptions import EmptyContentError, LLMClientError, MissingDependencyError
from gitmind.llm.base import LLMClient, MessageDefinition, MessageRole, ToolDefinition

try:
    from openai import NOT_GIVEN, OpenAIError
    from openai.types import ChatModel
    from openai.types.chat import (
        ChatCompletionMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionToolParam,
        ChatCompletionUserMessageParam,
    )
    from openai.types.chat.completion_create_params import ResponseFormat
    from openai.types.shared_params import FunctionDefinition

    if TYPE_CHECKING:
        from openai import AsyncClient
        from openai.lib.azure import AsyncAzureOpenAI
except ImportError as e:
    raise MissingDependencyError("openai is not installed") from e

__all__ = ["OpenAIClient"]

_openai_message_mapping: dict[MessageRole, type[ChatCompletionMessageParam]] = {
    "system": ChatCompletionSystemMessageParam,
    "user": ChatCompletionUserMessageParam,
}


class OpenAIClient(LLMClient):
    """Wrapper for OpenAI models.

    Args:
        api_key: The API key for the provider.
        model_name: The model to use for completions.
        endpoint_url: The endpoint URL for the provider.
        **kwargs: Additional keyword arguments.
    """

    _client: Union["AsyncAzureOpenAI", "AsyncClient"]
    """The OpenAI client instance."""
    _model: ChatModel | str
    """The model to use for generating completions."""

    __slots__ = ("_client", "_model")

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        endpoint_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        if deployment_id := kwargs.pop("deployment_id", None) and endpoint_url is not None:
            from openai.lib.azure import AsyncAzureOpenAI

            self._client = AsyncAzureOpenAI(
                azure_endpoint=endpoint_url,
                api_key=api_key,
                azure_deployment=cast(str, deployment_id),
                **kwargs,
            )
        else:
            from openai import AsyncClient

            self._client = AsyncClient(api_key=api_key, base_url=endpoint_url, **kwargs)
            self._model = model_name

    async def create_completions(
        self,
        *,
        messages: list[MessageDefinition],
        json_response: bool = False,
        tool: ToolDefinition | None = None,
        **kwargs: Any,
    ) -> str:
        """Create completions.

        Args:
            messages: The messages to generate completions for.
            json_response: Whether to return the response as a JSON object.
            tool: An optional tool call.
            **kwargs: Additional completion options.

        Raises:
            LLMClientError: If an error occurs while creating completions.
            EmptyContentError: If the LLM client returns empty content.

        Returns:
            The completion generated by the client.
        """
        try:
            result = await self._client.chat.completions.create(  # type: ignore[call-overload]
                model=self._model,
                messages=[
                    _openai_message_mapping[message.role](role=message.role, content=message.content)  # type: ignore[call-arg,arg-type]
                    for message in messages
                ],
                response_format=ResponseFormat(type="json_object" if json_response else "text"),
                stream=False,
                tools=[
                    ChatCompletionToolParam(
                        type="function",
                        function=FunctionDefinition(
                            name=tool.name,
                            parameters=tool.parameters,
                            description=tool.description or "",
                        ),
                    )
                ]
                if tool is not None
                else NOT_GIVEN,
                tool_choice="required" if tool else NOT_GIVEN,
                **kwargs,
            )
        except OpenAIError as e:
            raise LLMClientError("Failed to generate completion", context=str(e)) from e

        if content := result.choices[0].message.tool_calls[0].function.arguments:
            return cast(str, content)

        raise EmptyContentError("LLM client returned empty content", context=result.model_dump_json())
