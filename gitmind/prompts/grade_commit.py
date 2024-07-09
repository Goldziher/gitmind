from asyncio import gather
from typing import Any, Final, override

from gitmind.configuration_types import MessageDefinition, ToolDefinition
from gitmind.data_types import CommitGradingResult, CommitMetadata
from gitmind.prompts.base import AbstractPromptHandler
from gitmind.rules import DEFAULT_GRADING_RULES, Rule
from gitmind.utils.logger import get_logger

logger = get_logger(__name__)

GRADE_COMMIT_SYSTEM_MESSAGE: Final[str] = """
You are an assistant that grades git commits.

Evaluate the provided commit data and grade the commit according to the provided evaluation guidelines the commit.

- Be precise and concise.
- Do not use unnecessary superlatives.
- Do not include any code in the output.

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

        Returns:
            The grading results for the commit.
        """
        properties, evaluation_instructions = self.create_evaluation_instructions(grading_rules)

        commit_evaluation_prompt = (
            f"Evaluate and grade a git commit based on the following criteria:\n{evaluation_instructions}\n\n"
            f"**Commit Message**:{metadata["commit_message"]}\n\n"
            f"**Commit Diff**:\n"
        )

        tool = ToolDefinition(
            name="grading_results",
            description="Returns the grading results for a git commit.",
            parameters={
                "type": "object",
                "properties": properties,
            },
        )

        chunk_size = self._chunk_size - len(commit_evaluation_prompt)
        if len(diff) >= chunk_size:
            chunk_responses = await gather(
                *[
                    self.generate_completions(
                        properties=properties,
                        messages=[
                            MessageDefinition(role="system", content=GRADE_COMMIT_SYSTEM_MESSAGE),
                            MessageDefinition(role="user", content=commit_evaluation_prompt + diff[i : i + chunk_size]),
                        ],
                        tool=tool,
                    )
                    for i in range(0, len(diff), chunk_size)
                ]
            )
            final_response = await self.combine_results(results=list(chunk_responses), tool=tool, properties=properties)
        else:
            final_response = await self.generate_completions(
                properties=properties,
                messages=[
                    MessageDefinition(role="system", content=GRADE_COMMIT_SYSTEM_MESSAGE),
                    MessageDefinition(role="user", content=f"{commit_evaluation_prompt}{diff}"),
                ],
                tool=tool,
            )

        return [
            CommitGradingResult(rule_name=key, grade=value["grade"], reason=value["reasoning"])
            for (key, value) in final_response.items()
        ]

    @staticmethod
    def create_evaluation_instructions(grading_rules: list[Rule]) -> tuple[dict[str, Any], str]:
        """Create the evaluation instructions for the grading rules.

        Args:
            grading_rules: The grading rules to create evaluation instructions for.

        Returns:
            A tuple containing the properties and evaluation instructions.
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

        return properties, evaluation_instructions
