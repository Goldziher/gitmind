from typing import Any, Final, override

from inflection import titleize

from git_critic.configuration_types import MessageDefinition, ToolDefinition
from git_critic.data_types import CommitDescriptionResult, CommitMetadata, CommitStatistics
from git_critic.prompts.base import AbstractPromptHandler
from git_critic.utils.logger import get_logger
from git_critic.utils.serialization import serialize

logger = get_logger(__name__)

DESCRIBE_COMMIT_SYSTEM_MESSAGE: Final[str] = """
You are a helpful assistant that extracts information and describes the contents of git commits. Evaluate the provided
commit factoring in the context and provide a detailed description of the changes made in the commit. Be precise and
concise. Do not use unnecessary superlatives. Do not include any code in the output.

Respond by calling the provided tool 'describe_commit' with a JSON object adhering to its parameter definitions.
"""

DESCRIBE_COMMIT_PROPERTIES = {
    "summary": {"type": "string", "description": "Summary of the commit"},
    "purpose": {
        "type": "string",
        "description": "An estimation to the  purpose of the changes made in the commit and it's relative impact.",
    },
    "breakdown": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "file_name": {"type": "string", "description": "The name of the file"},
                "changes_description": {
                    "type": "string",
                    "description": "Description of the changes made in the file and their purpose",
                },
            },
            "required": ["file_name", "changes_description"],
        },
        "description": "Description of changes in each file and the purpose of the changes.",
    },
    "programming_languages_used": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of programming languages used in the commit",
    },
    "additional_notes": {"type": "string", "description": "Any additional relevant information"},
}


def titleize_commit_statistics(commit_statistics: CommitStatistics) -> str:
    """Titleize the commit statistics and render them as a string.

    Args:
        commit_statistics: The statistics of the commit.

    Returns:
        The extracted commit information.
    """
    infos = [
        f"- {titleize(key)}: {value}"
        for key, value in commit_statistics.items()
        if key != "per_files_changes" and value is not None
    ]

    return "\n".join(infos)


class DescribeCommitHandler(AbstractPromptHandler[CommitDescriptionResult]):
    """Handler for the describe commit prompt."""

    @override
    async def __call__(  # type: ignore[override]
        self,
        *,
        statistics: CommitStatistics,
        metadata: CommitMetadata,
        diff: str,
        **kwargs: Any,
    ) -> CommitDescriptionResult:
        """Generate completions for the describe commit prompt.

        Args:
            statistics: The statistics of the commit.
            metadata: The metadata of the commit.
            diff: The diff of the commit.
            retry_config: The retry configuration to use.
            **kwargs: Additional arguments.
        """
        prompt = (
            f"**Commit Message**:{metadata["commit_message"]}\n\n"
            f"**Commit Statistics**:\n{titleize_commit_statistics(statistics)}\n\n"
            f"**Per file breakdown**:\n{serialize(statistics["per_files_changes"]).decode()}\n\n"
            f"**Commit Diff**:\n{diff}"
        )
        parsed_response = await self.generate_completions(
            properties=DESCRIBE_COMMIT_PROPERTIES,
            messages=[
                MessageDefinition(
                    role="system",
                    content=DESCRIBE_COMMIT_SYSTEM_MESSAGE.strip(),
                ),
                MessageDefinition(role="user", content=prompt),
            ],
            json_response=True,
            tool=ToolDefinition(
                name="describe_commit",
                description="Returns the description for a git commit.",
                parameters={
                    "type": "object",
                    "properties": DESCRIBE_COMMIT_PROPERTIES,
                    "required": list(DESCRIBE_COMMIT_PROPERTIES.keys()),
                },
            ),
        )
        return CommitDescriptionResult(
            summary=parsed_response["summary"],
            purpose=parsed_response["purpose"],
            breakdown=parsed_response["breakdown"],
            programming_languages_used=parsed_response["programming_languages_used"],
            additional_notes=parsed_response["additional_notes"],
        )
