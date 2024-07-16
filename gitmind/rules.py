from __future__ import annotations

from pydantic import BaseModel


class Rule(BaseModel):
    """Base class for rules."""

    conditions: list[str] | None
    """Conditions for the rule."""
    evaluation_guidelines: str
    """The description of the rule."""
    name: str
    """The name of the rule."""
    title: str
    """The title of the rule."""


DEFAULT_GRADING_RULES = [
    Rule(
        name="coding_standards",
        title="Adherence to Coding Standards",
        evaluation_guidelines="Evaluate how well the commit adheres to the project's coding standards and guidelines.",
        conditions=None,
    ),
    Rule(
        name="commit_atomicity",
        title="Atomicity of the Commit",
        evaluation_guidelines="Evaluate whether the commit represents a single logical change.",
        conditions=[
            "The commit should not mix unrelated changes.",
        ],
    ),
    Rule(
        name="code_quality",
        title="Code Quality",
        evaluation_guidelines="Evaluate the quality of the code or code-related changes in the commit.",
        conditions=[
            "The changes should be well-implemented, following best practices, and they should not introduce new issues or bugs.",
            "This rule should only be evaluated when the changes in the commit affect code, scripts, and configurations.",
        ],
    ),
    Rule(
        name="message_quality",
        title="Commit Message Quality",
        evaluation_guidelines="Evaluate the quality of the commit message.",
        conditions=[
            "The commit message should fit the changes made in the commit. It should be relevant and accurate. It should not be misleading.",
        ],
    ),
    Rule(
        name="documentation_quality",
        title="Documentation Quality",
        evaluation_guidelines="Evaluate the quality of the documentation included with the commit.",
        conditions=[
            "Documentation should be clear, concise, and informative.",
            "Documentation changes should only be evaluated when the changes in the commit affect code or configurations that should be documented.",
        ],
    ),
    Rule(
        name="codebase_impact",
        title="Impact on the Codebase",
        evaluation_guidelines="Evaluate the impact of the commit on the overall codebase.",
        conditions=None,
    ),
    Rule(
        name="changes_scope",
        title="Scope of Changes",
        evaluation_guidelines="Evaluate the appropriateness of the scope of changes in the commit.",
        conditions=None,
    ),
    Rule(
        name="test_quality",
        title="Test Quality",
        evaluation_guidelines="Evaluate the quality and coverage of the tests included with the commit.",
        conditions=[
            "Testing coverage should be graded only when the changes in the commit affect code that should be tested. This excludes testing code itself and scripts like bash that are not commonly unit-tested.",
            "Evaluate the quality of the tests, not just the quantity.",
            "Duplication of code in tests is not considered an issue.",
        ],
    ),
    Rule(
        name="triviality",
        title="Triviality of Commit Changes",
        evaluation_guidelines="Evaluate whether the commit contains significant or trivial changes.",
        conditions=[
            "Trivial changes do not significantly affect the codebase or introduce new functionality.",
            "Significant changes improve the codebase, fix bugs, or add new features.",
        ],
    ),
]
