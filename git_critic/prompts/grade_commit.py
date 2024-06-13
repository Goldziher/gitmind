from typing import Any, Final, override

from git_critic.configuration_types import MessageDefinition, ToolDefinition
from git_critic.data_types import CommitGradingResult, CommitMetadata
from git_critic.prompts.base import AbstractPromptHandler
from git_critic.rules import DEFAULT_GRADING_RULES, Rule
from git_critic.utils.logger import get_logger

logger = get_logger(__name__)

GRADE_COMMIT_SYSTEM_MESSAGE: Final[str] = """
You are a helpful assistant that grades git commits. Evaluate the provided commit factoring in the context in grading
the commit. Be precise and concise. Do not use unnecessary superlatives. Do not include any code in the output.

Respond by calling the provided tool 'grading_results' with a JSON object adhering to its parameter definitions.
"""


class GradeCommitHandler(AbstractPromptHandler[list[CommitGradingResult]]):
    """Handler for grading a git commit."""

    @override
    async def __call__(  # type: ignore[override]
        self,
        *,
        metadata: CommitMetadata,
        diff: str,
        grading_rules: list[Rule] = DEFAULT_GRADING_RULES,
    ) -> list[CommitGradingResult]:
        """Generate LLM completions for grading a git commit.

        Args:
            metadata: The metadata of the commit.
            diff: The diff of the commit.
            grading_rules: The grading rules to use.
            retry_config: The retry configuration to use.

        Returns:
            The grading results for the commit.
        """
        properties: dict[str, Any] = {}

        evaluation_instructions = ""

        for grading_rule in grading_rules:
            additional_conditions = ""
            if grading_rule.conditions:
                for condition in grading_rule.conditions:
                    additional_conditions += f"        - {condition}\n"

            description = f"""
            ##{grading_rule.title}##

            ###Evaluation Guidelines###
            {grading_rule.evaluation_guidelines}

            ####Additional Evaluation Conditions####
            {additional_conditions or "None"}
            """

            evaluation_instructions += f"**{grading_rule.title}**\n"
            evaluation_instructions += description

            properties[grading_rule.name] = {
                "description": description,
                "title": grading_rule.title,
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

        prompt = (
            f"Evaluate and grade a git commit based on the following criteria:\n{evaluation_instructions}\n\n"
            f"**Commit Message**:{metadata["commit_message"]}\n\n"
            f"**Commit Diff**:\n{diff}"
        )

        parsed_response = await self.generate_completions(
            properties=properties,
            messages=[
                MessageDefinition(role="system", content=GRADE_COMMIT_SYSTEM_MESSAGE),
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

        return [
            CommitGradingResult(rule_name=key, grade=value["grade"], reason=value["reasoning"])
            for (key, value) in parsed_response.items()
        ]
