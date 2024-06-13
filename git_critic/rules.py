from pydantic import BaseModel


class Rule(BaseModel):
    """Base class for rules."""

    conditions: list[str] | None
    """Conditions for the rule."""
    evaluation_guidelines: str
    """The description of the rule."""
    max_grade_description: str
    """The maximum grade for the rule."""
    min_grade_description: str
    """The minimum grade for the rule."""
    name: str
    """The name of the rule."""
    title: str
    """The title of the rule."""
    weight: float = 1.0
    """The weight of the rule."""


DEFAULT_GRADING_RULES = [
    Rule(
        name="coding_standards",
        title="Adherence to Coding Standards",
        evaluation_guidelines="Evaluate how well the commit adheres to the project's coding standards and guidelines.",
        conditions=None,
        min_grade_description="The changes do not follow the project's coding standards and guidelines.",
        max_grade_description="The changes strictly adhere to the project's coding standards and guidelines.",
    ),
    Rule(
        name="commit_atomicity",
        title="Atomicity of the Commit",
        evaluation_guidelines="Evaluate whether the commit represents a single logical change.",
        conditions=[
            "The commit should not mix unrelated changes.",
            "Trivial changes such as whitespace changes and typo fixes should not be factored into the evaluation.",
        ],
        min_grade_description="The commit mixes unrelated changes.",
        max_grade_description="The commit is atomic, representing a single logical change.",
    ),
    Rule(
        name="code_quality",
        title="Code Quality",
        evaluation_guidelines="Evaluate the quality of the code or code-related changes in the commit.",
        conditions=[
            "The changes should be well-implemented, following best practices.",
            "The changes should not introduce new issues or bugs.",
            "This rule should only be evaluated when the changes in the commit affect code, scripts, and configurations.",
        ],
        min_grade_description="The changes introduce new issues or are of poor quality.",
        max_grade_description="The changes are well-implemented, improve the codebase, and follow best practices.",
    ),
    Rule(
        name="message_quality",
        title="Commit Message Quality",
        evaluation_guidelines="Evaluate the quality of the commit message.",
        conditions=[
            "The commit message should fit the changes made in the commit.",
            "The commit message should not be misleading or inaccurate.",
            "The commit message should be concise but descriptive.",
            "The commit message should not be vague or generic, e.g., 'fix code', 'remove two files' etc.",
            "The standard maximal length of a commit message in GitHub is 72 characters; this should be taken into account.",
        ],
        min_grade_description="The commit message is vague, misleading, or inaccurate.",
        max_grade_description="The commit message is clear, concise, and accurately describes the changes made.",
    ),
    Rule(
        name="documentation_quality",
        title="Documentation Quality",
        evaluation_guidelines="Evaluate the quality of the documentation included with the commit.",
        conditions=[
            "Documentation should be clear, concise, and informative.",
            "Documentation changes should only be evaluated when the changes in the commit affect code or configurations that should be documented.",
        ],
        min_grade_description="The commit lacks necessary documentation or has poor-quality documentation.",
        max_grade_description="The commit includes thorough, clear, and helpful documentation that accurately describes the changes and their purpose.",
    ),
    Rule(
        name="codebase_impact",
        title="Impact on the Codebase",
        evaluation_guidelines="Evaluate the impact of the commit on the overall codebase.",
        conditions=None,
        min_grade_description="The commit negatively impacts the codebase, introducing bugs or issues.",
        max_grade_description="The commit positively impacts the codebase, such as fixing bugs, improving performance, or adding valuable features.",
    ),
    Rule(
        name="changes_scope",
        title="Scope of Changes",
        evaluation_guidelines="Evaluate the appropriateness of the scope of changes in the commit.",
        conditions=None,
        min_grade_description="The commit is either too large and unwieldy or too small and trivial.",
        max_grade_description="The commit has an appropriate scope, addressing a specific issue or feature comprehensively.",
    ),
    Rule(
        name="test_quality",
        title="Test Quality",
        evaluation_guidelines="Evaluate the quality and coverage of the tests included with the commit.",
        conditions=[
            "Testing coverage should be graded only when the changes in the commit affect code that should be tested.",
            "Code that should be tested excludes testing code itself and scripts like bash that are not commonly unit-tested.",
            "Evaluate the quality of the tests, not just the quantity.",
            "Duplication of code in tests is not considered an issue as long as the tests cover different aspects of the code.",
        ],
        min_grade_description="The commit lacks sufficient tests, and changes may break existing functionality.",
        max_grade_description="The commit includes comprehensive tests, validating the new functionality and ensuring existing functionality remains unaffected.",
    ),
    Rule(
        name="triviality",
        title="Triviality of Commit Changes",
        evaluation_guidelines="Evaluate whether the commit contains significant or trivial changes.",
        conditions=[
            "Trivial changes do not significantly affect the codebase or introduce new functionality.",
            "Significant changes improve the codebase, fix bugs, or add new features.",
            "Trivial changes may include whitespace changes, typo fixes, or other minor adjustments.",
        ],
        min_grade_description="The commit is overly trivial, containing insignificant changes.",
        max_grade_description="The commit contains significant, meaningful changes.",
    ),
]
