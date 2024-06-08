from typing import Any

from msgspec import DecodeError

from src.data_types import CommitDataDTO, CommitGradingResult, Rule
from src.exceptions import CriticError, LLMClientError
from src.llm.base import LLMClient, Message
from src.rules import DEFAULT_GRADING_RULES
from src.utils.logger import get_logger
from src.utils.serialization import deserialize, serialize

logger = get_logger(__name__)


async def describe_commit_contents(
    *,
    client: LLMClient,
    commit_data: CommitDataDTO,
) -> str:
    """Describe the contents of a commit.

    Args:
        client: The OpenAI client to use.
        commit_data: The data of the commit.

    Returns:
        The description of the commit contents.
    """
    prompt = f"""
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
            Message(
                role="system",
                content=system_message,
            ),
            Message(role="user", content=prompt),
        ],
    )
    logger.debug(
        "Received content from OpenAI for describe commit contents request with the following content: %s",
        completion,
    )
    return completion


async def grade_commit(
    *,
    client: LLMClient,
    commit_data: CommitDataDTO,
    commit_description: str,
    grading_rules: list[Rule] | None = None,
) -> list[CommitGradingResult]:
    """Grade a commit.

    Args:
        client: The OpenAI client to use.
        commit_data: The data of the commit.
        commit_description: The description of the commit.
        grading_rules: The grading rules to use.

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
        result = await client.create_completions(
            messages=[
                Message(role="system", content="You are a helpful assistant that grades git commits."),
                Message(role="user", content=prompt),
            ],
            json_response=True,
        )

        logger.debug(
            "Received content from OpenAI for grade commit request with the following content: %s",
            result,
        )
        result_dict = deserialize(result, dict)
        return [
            CommitGradingResult(rule_name=key, grade=value["grade"], reason=value["reasoning"])
            for (key, value) in result_dict.items()
            if key in properties
        ]
    except (DecodeError, LLMClientError) as e:
        logger.error("Error occurred while grading commit: %s.", e)
        raise CriticError("Error occurred while grading commit.") from e
