from typing import Final, Literal, TypedDict, override

from gitmind.llm.base import MessageDefinition, ToolDefinition
from gitmind.prompts.base import AbstractPromptHandler
from gitmind.rules import DEFAULT_GRADING_RULES, Rule
from gitmind.utils.commit import CommitMetadata
from gitmind.utils.serialization import serialize


class CommitGradingResult(TypedDict):
    """DTO for grading results."""

    grade: int | Literal["NOT_EVALUATED"]
    """The grade for the commit."""
    reason: str
    """The reason for the grade."""


GRADE_COMMIT_SYSTEM_MESSAGE: Final[str] = """
You are an assistant that grades git commits.

Evaluate the provided commit data and grade the commit according to the provided evaluation guidelines.

Response instructions:

- Be concise and factual.
- Do not use unnecessary superlatives.
- Do not include any code in the output.

Respond by calling the provided tool 'grading_results' with a JSON object adhereing to the following JSON schema:

```json
{schema}
```
"""


class GradeCommitHandler(AbstractPromptHandler[dict[str, CommitGradingResult]]):
    """Handler for grading a git commit."""

    @override
    async def __call__(  # type: ignore[override]
        self,
        *,
        metadata: CommitMetadata,
        diff: str,
        grading_rules: list[Rule] = DEFAULT_GRADING_RULES,
    ) -> dict[str, CommitGradingResult]:
        """Generate LLM completions for grading a git commit.

        Args:
            metadata: The metadata of the commit.
            diff: The diff of the commit.
            grading_rules: The grading rules to use.

        Returns:
            The grading results for the commit.
        """
        evaluation_instructions = self.create_evaluation_instructions(grading_rules)

        commit_evaluation_prompt = (
            f"Evaluate and grade a git commit based on the following criteria:\n{evaluation_instructions}\n\n"
            f"**Commit Message**:{metadata["message"]}\n\n"
            f"**Commit Diff**:\n{diff}"
        )

        object_type = {
            "type": "object",
            "properties": {
                "grade": {
                    "oneOf": [
                        {"type": "integer", "minimum": 1, "maximum": 10},
                        {"const": "NOT_EVALUATED"},
                    ]
                },
                "reason": {"type": "string"},
            },
            "required": ["grade", "reason"],
        }

        schema = {
            "type": "object",
            "properties": {rule.name: object_type for rule in grading_rules},
            "required": [rule.name for rule in grading_rules],
        }

        tool = ToolDefinition(
            name="grading_results",
            description="Returns the grading results for a git commit.",
            parameters=schema,
        )

        result = await self.generate_completions(
            response_type=dict[str, CommitGradingResult],
            schema=schema,
            messages=[
                MessageDefinition(
                    role="system",
                    content=GRADE_COMMIT_SYSTEM_MESSAGE.format(
                        schema=serialize(
                            {
                                "$schema": "http://json-schema.org/draft-07/schema#",
                                **schema,
                            },
                        ),
                    ),
                ),
                MessageDefinition(role="user", content=commit_evaluation_prompt),
            ],
            tool=tool,
        )

        return dict(sorted(result.items()))

    @staticmethod
    def create_evaluation_instructions(grading_rules: list[Rule]) -> str:
        """Create the evaluation instructions for the grading rules.

        Args:
            grading_rules: The grading rules to create evaluation instructions for.

        Returns:
            A tuple containing the properties and evaluation instructions.
        """
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

            evaluation_instructions += description

        return evaluation_instructions
