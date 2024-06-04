from itertools import chain
from typing import TYPE_CHECKING, Any, ClassVar, Final, Optional

from msgspec import DecodeError
from openai import OpenAIError
from openai.types import ChatModel
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from exceptions import CriticError
from src.rules import DEFAULT_GRADING_RULES
from src.types import CommitDataDTO, CommitGradingResult, Rule
from src.utils.serialization import deserialize, serialize
from utils.logger import get_logger

logger = get_logger(__name__)


if TYPE_CHECKING:
    from collections.abc import Iterable

    from openai import AsyncClient as AsyncOpenAI
    from openai.lib.azure import AsyncAzureOpenAI


class OpenAIClient:
    """Wrapper for OpenAI models."""

    _instance: ClassVar[Optional["OpenAIClient"]] = None

    __slots__ = ("_client", "_default_model")

    def __init__(
        self, *, api_key: str, base_url: str, default_model: ChatModel, use_azure: bool = False, **kwargs: Any
    ) -> None:
        """Initialize the OpenAI model.

        Args:
            api_key: The API key for the OpenAI model.
            base_url: The base URL for the OpenAI model.
            default_model: The default model to use for requests in case a model is not provided.
            use_azure: Whether to use Azure OpenAI.
            **kwargs: Additional keyword arguments to pass to the OpenAI client.
        """
        if use_azure:
            from openai.lib.azure import AsyncAzureOpenAI as AsyncClient
        else:
            from openai import AsyncClient  # type: ignore[assignment]

        self._client: AsyncOpenAI | AsyncAzureOpenAI = AsyncClient(api_key=api_key, base_url=base_url, **kwargs)
        self._default_model: Final[ChatModel] = default_model

    @classmethod
    def create_instance(
        cls, api_key: str, base_url: str, default_model: ChatModel, use_azure: bool = False, **kwargs: Any
    ) -> "OpenAIClient":
        """Create a singleton instance of the class.

        Args:
            api_key: The API key for the OpenAI model.
            base_url: The base URL for the OpenAI model.
            default_model: The default model to use for requests in case a model is not provided.
            use_azure: Whether to use Azure OpenAI.
            **kwargs: Additional keyword arguments to pass to the OpenAI client.

        Returns:
            OpenAIClient: The singleton instance of the class.
        """
        cls._instance = cls(
            api_key=api_key, base_url=base_url, default_model=default_model, use_azure=use_azure, **kwargs
        )
        return cls._instance

    @classmethod
    def get_instance(cls) -> "OpenAIClient":
        """Get the singleton instance of the class.

        Raises:
            ValueError: If the instance has not been initialized.

        Returns:
            OpenAIClient: The singleton instance of the class.
        """
        if cls._instance is None:
            raise ValueError("Instance has not been initialized. Call '.create_instance' before calling get.")
        return cls._instance

    async def describe_commit_contents(
        self,
        *,
        commit_data: CommitDataDTO,
        model: ChatModel | None = None,
    ) -> str:
        """Describe the contents of a commit.

        Args:
            commit_data: The data of the commit.
            model: The AI model to use for the request description.

        Returns:
            The description of the commit contents.
        """
        prompt = f"""
        Describe in detail the changes made in the following git commit.

        Here are the totals for the commit:

        - Total files changed: {commit_data["total_files_changed"]}
        - Total lines changed: {commit_data["total_lines_changed"]}

        Here are the overall statistics for the commit:

        - Additions: {commit_data["num_additions"]}
        - Deletions: {commit_data["num_deletions"]}
        - Copies: {commit_data["num_copies"]}
        - Modifications: {commit_data["num_modifications"]}
        - Renames: {commit_data["num_renames"]}
        - Type changes: {commit_data["num_type_changes"]}

        Here is a file by file breakdown: {serialize(commit_data["per_files_changes"]).decode()}

        Here are the contents of the diff: {commit_data["diff_contents"]}
        """

        logger.debug("Sending describe commit contents request with the following prompt:\n\n%s", prompt)

        response = await self._client.chat.completions.create(
            model=model if model is not None else self._default_model,
            messages=(
                ChatCompletionSystemMessageParam(
                    role="system", content="You are a helpful assistant that describes the content of git commits."
                ),
                ChatCompletionUserMessageParam(role="user", content=prompt),
            ),
        )

        if response.choices and (response_content := response.choices[0].message.content):
            logger.debug(
                "Received content from OpenAI for describe commit contents request with the following content: %s",
                response_content,
            )
            return response_content

        logger.warning("No content received from OpenAI for describe commit contents request.")
        return ""

    async def grade_commit(
        self,
        *,
        commit_data: CommitDataDTO,
        commit_description: str,
        grading_rules: list[Rule] | None,
        model: ChatModel | None = None,
    ) -> list[CommitGradingResult]:
        """Grade a commit.

        Args:
            commit_data: The data of the commit.
            commit_description: The description of the commit.
            grading_rules: The grading rules to use.
            model: The AI model to use for grading.

        Returns:
            The grade for the commit.
        """
        properties: dict[str, Any] = {}

        evaluation_instructions = ""

        rules = grading_rules or DEFAULT_GRADING_RULES

        for grading_rule in rules:
            additional_conditions = ""
            if grading_rule["additional_conditions"]:
                for condition in grading_rule["additional_conditions"]:
                    additional_conditions += f"        - {condition}\n"

            description = f"""
            ##{grading_rule['title']}##

            ###Evaluation Guidelines###
            {grading_rule["evaluation_guidelines"]}

            ####Additional Evaluation Conditions####
            {additional_conditions or "None"}

            ###Grade Descriptions###
            **Minimum grade description**: {grading_rule["min_grade_description"]}
            **Maximum grade description**: {grading_rule["max_grade_description"]}
            """

            evaluation_instructions += f"**{grading_rule['title']}**\n"
            evaluation_instructions += description

            properties[grading_rule["name"]] = {
                "description": description,
                "title": grading_rule["title"],
                "type": "object",
                "properties": {
                    "grade": {
                        "oneOf": [
                            {
                                "description": "The grade for this rule. 1 is the lowest, 10 is the highest.",
                                "maximum": 10,
                                "minimum": 1,
                                "type": "integer",
                            },
                            {
                                "description": "The rule was not evaluated because the contents of the commit do not fit the rule's conditions.",
                                "const": "NOT_EVALUATED",
                            },
                        ]
                    },
                    "reasoning": {
                        "description": "The reasoning for the grade given, or if the rule is not evaluated, an explanation why.",
                        "type": "string",
                    },
                },
            }

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Commit Evaluation Result",
            "type": "object",
            "properties": properties,
        }

        prompt = f"""Your task is to evaluate and grade a git commit based on the following criteria:

        {evaluation_instructions}

        The return value for this function should be a JSON object that adheres to the following schema JSON schema:

        {serialize(json_schema).decode()}

        Here is the description of the commit: {commit_description}

        And here is the data extracted from the commit: {serialize(commit_data).decode()}
        """

        logger.debug("Sending grade commit request with the following prompt:\n\n%s", prompt)

        try:
            response = await self._client.chat.completions.create(
                model=model if model is not None else self._default_model,
                messages=(
                    ChatCompletionSystemMessageParam(
                        role="system", content="You are a helpful assistant that grades git commits."
                    ),
                    ChatCompletionUserMessageParam(role="user", content=prompt),
                ),
                response_format={
                    "type": "json_object",
                },
            )

            if not response.choices or not response.choices[0].message.content:
                raise CriticError("No content received from OpenAI for grade commit request.")

            logger.debug(
                "Received content from OpenAI for grade commit request with the following content: %s",
                response.choices[0].message.content,
            )
            results: Iterable[tuple[str, dict]] = chain(
                *[list(datum.items()) for datum in deserialize(response.choices[0].message.content, list[dict])]
            )

            return [
                CommitGradingResult(rule_name=key, grade=value["grade"], reason=value["reasoning"])
                for key, value in results
            ]
        except (DecodeError, OpenAIError) as e:
            logger.error("Error occurred while grading commit: %s.", e)
            raise CriticError("Error occurred while grading commit.") from e
