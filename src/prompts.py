from src.models import AIModel
from src.rules import DEFAULT_GRADING_RULES
from src.types import CommitDataDTO, Rule
from src.utils.serialization import serialize


async def describe_commit_contents(
    *,
    commit_data: CommitDataDTO,
    model: AIModel,
) -> str:
    """Describe the contents of a commit.

    Args:
        commit_data: The data of the commit.
        model: The AI model to use for description.

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

    return await model.prompt(prompt)


async def grade_commit(
    *,
    commit_data: CommitDataDTO,
    commit_description: str,
    grading_rules: list[Rule] | None,
    model: AIModel,
):
    """Grade a commit.

    Args:
        commit_data: The data of the commit.
        commit_description: The description of the commit.
        grading_rules: The grading rules to use.
        model: The AI model to use for grading.

    Returns:
        The grade for the commit.
    """
    return_value_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Commit Evaluation Result",
        "type": "object",
    }

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

        return_value_schema["properties"][grading_rule["name"]] = {
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

    The return value for this function should be a JSON object that adheres to the following schema JSON schema:

    {serialize(return_value_schema).decode()}

    Here is the description of the commit: {commit_description}

    And here is the data extracted from the commit: {serialize(commit_data).decode()}
    """

    return await model.prompt(prompt)
