from typing import Any

from anyio import sleep
from inflection import titleize
from msgspec import DecodeError

from git_critic.configuration_types import CommitGradingConfig, MessageDefinition, ToolDefinition
from git_critic.data_types import CommitDataDTO, CommitGradingResult
from git_critic.exceptions import LLMClientError
from git_critic.llm.base import LLMClient
from git_critic.utils.logger import get_logger
from git_critic.utils.serialization import deserialize, serialize

logger = get_logger(__name__)


async def describe_commit_contents(
    *,
    client: LLMClient,
    commit_data: CommitDataDTO,
    diff_contents: str,
) -> str:
    """Describe the contents of a commit.

    Args:
        client: The OpenAI client to use.
        commit_data: The data of the commit.
        diff_contents: The contents of the diff.

    Returns:
        The description of the commit contents.
    """
    try:
        commit_info = [
            f"- {titleize(key)}: {value}"
            for key, value in commit_data.items()
            if key
            not in {
                "commit_author_email",
                "commit_author_name",
                "commit_commiter_email",
                "commit_commiter_name",
                "commit_authored_timestamp",
                "commit_commited_timestamp",
                "commit_hash",
                "parent_commit_hash",
                "per_files_changes",
            }
            and value is not None
        ]

        prompt = f"""
            Commit Info:
            {'\n'.join(commit_info)}

            Per file breakdown:
            {serialize(commit_data["per_files_changes"]).decode()}

            Commit Diff Contents:
            {diff_contents}
            """

        logger.debug("Sending describe commit contents request with the following prompt:\n\n%s", prompt)

        system_message = """
            You are a helpful assistant that describes the content of git commits.  Upon receiving a user message evaluate
            the commit provided factoring in all context and provide a detailed description of the changes made in the
            commit. The description is meant to be used by an LLM rather than a human and your response should optimize
            for this.
            Be precise and concise. Do not include code unless the code is necessary to describe the commit. Even in
            this case, the code should be minimal and only used to explain a point. Any statistics provided should be
            accurate and and comprehensive.
        """

        completion = await client.create_completions(
            messages=[
                MessageDefinition(
                    role="system",
                    content=system_message,
                ),
                MessageDefinition(role="user", content=prompt),
            ],
        )
        logger.debug(
            "Received content from OpenAI for describe commit contents request with the following content: %s",
            completion,
        )
        return completion
    except LLMClientError as e:
        logger.error("Error occurred while describing commit: %s.", e)
        raise


async def grade_commit(
    *,
    client: LLMClient,
    commit_data: CommitDataDTO,
    commit_description: str,
    config: CommitGradingConfig,
    retry_count: int = 0,
) -> list[CommitGradingResult]:
    """Grade a commit.

    Args:
        client: The OpenAI client to use.
        commit_data: The data of the commit.
        commit_description: The description of the commit.
        config: The grading configuration.
        retry_count: The number of times to retry the grading.

    Returns:
        The grade for the commit.
    """
    properties: dict[str, Any] = {}

    evaluation_instructions = ""

    for grading_rule in config.grading_rules:
        additional_conditions = ""
        if grading_rule["conditions"]:
            for condition in grading_rule["conditions"]:
                additional_conditions += f"        - {condition}\n"

        description = f"""
        ##{grading_rule['title']}##

        ###Evaluation Guidelines###
        {grading_rule["evaluation_guidelines"]}

        ####Additional Evaluation Conditions####
        {additional_conditions or "None"}
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

    prompt = f"""Your task is to evaluate and grade a git commit based on the following criteria:

    {evaluation_instructions}

    Here is the description of the commit: {commit_description}

    And here is the data extracted from the commit: {serialize(commit_data).decode()}

    Respond by calling the provided tool 'grading_results' with an object adhering to its parameter definitions.
    """

    logger.debug("Sending grade commit request with the following prompt:\n\n%s", prompt)

    try:
        result = await client.create_completions(
            messages=[
                MessageDefinition(role="system", content="You are a helpful assistant that grades git commits."),
                MessageDefinition(role="user", content=prompt),
            ],
            json_response=True,
            tool=ToolDefinition(
                name="grading_results",
                description="Returns the grading results for a git commit.",
                parameters={
                    "type": "object",
                    "properties": properties,
                },
            ),
            max_tokens=4096,
        )

        logger.debug(
            "Received content from OpenAI for grade commit request with the following content: %s",
            result,
        )

        return [
            CommitGradingResult(rule_name=key, grade=value["grade"], reason=value["reasoning"])
            for (key, value) in deserialize(result, dict).items()
            if key in properties and "grade" in value and "reasoning" in value
        ]
    except LLMClientError as e:
        logger.error("Error occurred while grading commit: %s.", e)
        raise
    except DecodeError as e:
        # Retry grading if the response is invalid JSON
        # This has to be in place because LLMs sometimes return invalid JSON
        if retry_count < config.retry_config.max_retries:
            retry_count += 1
            logger.warning(
                "LLM responded with invalid JSON, retrying (%d/%d)", retry_count, config.retry_config.max_retries
            )
            await sleep((2**retry_count) if config.retry_config.exponential_backoff else 1)
            return await grade_commit(
                client=client,
                commit_data=commit_data,
                commit_description=commit_description,
                config=config,
                retry_count=retry_count,
            )
        logger.warning("LLM responded with invalid JSON, retrying")
        raise LLMClientError(
            f"LLM responded with invalid JSON all grading attempts for commit {commit_data["commit_hash"]}",
            context=str(e),
        ) from e
