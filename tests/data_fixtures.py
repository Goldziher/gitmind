describe_commit_response = """The commit reflects systematic updates and refinements across various files in the codebase, involving multiple types of
changes without any net additions or deletions in terms of functionality. The changes span 14 files and total 14 lines
of modifications. Below is a detailed breakdown by file and the nature of changes:

### File-by-File Breakdown

1. **`.env`**
    - **Insertions:** 1
    - Removed sensitive information, specifically a hardcoded OpenAI API key.

2. **`.gitignore`**
    - **Insertions:** 1
    - Adjusted ignored files, specifically by removing `.env` from the list.

3. **`e2e/__init__.py`**
    - No changes made.

4. **`e2e/test_describe_commit.py`**
    - **Deletions:** 42
    - The entire test file was removed. This file contained an asynchronous test function for describing commits using
      OpenAI’s API.

5. **`pdm.lock`**
    - **Insertions:** 12
    - **Deletions:** 1
    - Updated dependencies and the content hash, reflecting library version changes and removal of the `python-dotenv`
      package.

6. **`pyproject.toml`**
    - **Insertions:** 6
    - Adjusted dependencies and configurations, likely aligning them with changes in other parts of the project.

7. **`src/commit.py`**
    - **Insertions:** 2
    - **Deletions:** 2
    - Modified import paths and the internals of `extract_commit_data` method for better consistency and possibly to
      rectify errors.

8. **`src/llm/base.py`**
    - **Insertions:** 1
    - **Deletions:** 1
    - Minor method signature change from synchronous initialization to asynchronous (`init` method).

9. **`src/llm/openai_client.py`**
    - **Insertions:** 37
    - **Deletions:** 18
    - Significant revisions to support more robust interaction with OpenAI API, including updated response handling and
      improved error management.

10. **`src/llm/result.md`**
    - **Insertions:** 86
    - Added detailed documentation or result markdown about the changes for
      commit `d63b4db42993cd0e5262f79a62c022d09c051eef`.

11. **`src/prompts.py`**
    - **Insertions:** 3
    - **Deletions:** 3
    - Adjusted import paths and possibly refined methods for consistency and performance.

12. **`src/repository.py`**
    - **Insertions:** 6
    - **Deletions:** 6
    - Updated method signatures and internal variables for correctness and perhaps simplifying usage patterns.

13. **`src/types.py`**
    - **Insertions:** 3
    - **Deletions:** 1
    - Minor adjustments to types to ensure alignment with the broader refactor.

14. **`src/utils/serialization.py`**
    - **Insertions:** 1
    - **Deletions:** 1
    - Adjusted serialization utility to use sorted order for encoding.

### Key Objectives

- **Refactoring & Cleanup**:
    - Removed hardcoded credentials and sensitive information.
    - Removed outdated or unused test functions and dependencies.
    - Simplified and corrected import paths and method signatures.

- **Improved Code Consistency**:
    - Ensured consistency in method signatures and variable naming conventions.
    - Applied changes uniformly across related modules, e.g., LLM-related classes and methods.

- **Library and Dependency Updates**:
    - Updated dependencies in `pdm.lock` and `pyproject.toml`, including removing the `python-dotenv` library,
      reflecting a move away from using `.env` files for configuration.

### Summary

This commit is a comprehensive maintenance and refactor, enhancing code quality, security, and consistency. Major
aspects include removal of sensitive hardcoding, dependency cleanup, and rigorous alignment of import paths and method
conventions across the codebase."""

grade_commit_response = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Commit Evaluation Result",
    "type": "object",
    "properties": {
        "coding_standards": {
            "description": "##Adherence to Coding Standards## ###Evaluation Guidelines### Evaluate how well the commit adheres to the project's coding standards and guidelines. ####Additional Evaluation Conditions#### None ###Grade Descriptions### **Minimum grade description**: The changes do not follow the project's coding standards and guidelines. **Maximum grade description**: The changes strictly adhere to the project's coding standards and guidelines.",
            "title": "Adherence to Coding Standards",
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
        },
        "commit_atomicity": {
            "description": "##Atomicity of the Commit## ###Evaluation Guidelines### Evaluate whether the commit represents a single logical change. ####Additional Evaluation Conditions#### - The commit should not mix unrelated changes. - Trivial changes such as whitespace changes and typo fixes should not be factored into the evaluation. ###Grade Descriptions### **Minimum grade description**: The commit mixes unrelated changes. **Maximum grade description**: The commit is atomic, representing a single logical change.",
            "title": "Atomicity of the Commit",
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
        },
        "code_quality": {
            "description": "##Code Quality## ###Evaluation Guidelines### Evaluate the quality of the code or code-related changes in the commit. ####Additional Evaluation Conditions#### - The changes should be well-implemented, following best practices. - The changes should not introduce new issues or bugs. - This rule should only be evaluated when the changes in the commit affect code, scripts, and configurations. ###Grade Descriptions### **Minimum grade description**: The changes introduce new issues or are of poor quality. **Maximum grade description**: The changes are well-implemented, improve the codebase, and follow best practices.",
            "title": "Code Quality",
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
        },
        "message_quality": {
            "description": "##Commit Message Quality## ###Evaluation Guidelines### Evaluate the quality of the commit message. ####Additional Evaluation Conditions#### - The commit message should fit the changes made in the commit. - The commit message should not be misleading or inaccurate. - The commit message should be concise but descriptive. - The commit message should not be vague or generic, e.g., 'fix code', 'remove two files' etc. - The standard maximal length of a commit message in GitHub is 72 characters; this should be taken into account. ###Grade Descriptions### **Minimum grade description**: The commit message is vague, misleading, or inaccurate. **Maximum grade description**: The commit message is clear, concise, and accurately describes the changes made.",
            "title": "Commit Message Quality",
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
        },
        "documentation_quality": {
            "description": "##Documentation Quality## ###Evaluation Guidelines### Evaluate the quality of the documentation included with the commit. ####Additional Evaluation Conditions#### - Documentation should be clear, concise, and informative. - Documentation changes should only be evaluated when the changes in the commit affect code or configurations that should be documented. ###Grade Descriptions### **Minimum grade description**: The commit lacks necessary documentation or has poor-quality documentation. **Maximum grade description**: The commit includes thorough, clear, and helpful documentation that accurately describes the changes and their purpose.",
            "title": "Documentation Quality",
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
        },
        "codebase_impact": {
            "description": "##Impact on the Codebase## ###Evaluation Guidelines### Evaluate the impact of the commit on the overall codebase. ####Additional Evaluation Conditions#### None ###Grade Descriptions### **Minimum grade description**: The commit negatively impacts the codebase, introducing bugs or issues. **Maximum grade description**: The commit positively impacts the codebase, such as fixing bugs, improving performance, or adding valuable features.",
            "title": "Impact on the Codebase",
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
        },
        "changes_scope": {
            "description": "##Scope of Changes## ###Evaluation Guidelines### Evaluate the appropriateness of the scope of changes in the commit. ####Additional Evaluation Conditions#### None ###Grade Descriptions### **Minimum grade description**: The commit is either too large and unwieldy or too small and trivial. **Maximum grade description**: The commit has an appropriate scope, addressing a specific issue or feature comprehensively.",
            "title": "Scope of Changes",
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
        },
        "test_quality": {
            "description": "##Test Quality## ###Evaluation Guidelines### Evaluate the quality and coverage of the tests included with the commit. ####Additional Evaluation Conditions#### - Testing coverage should be graded only when the changes in the commit affect code that should be tested. - Code that should be tested excludes testing code itself and scripts like bash that are not commonly unit-tested. - Evaluate the quality of the tests, not just the quantity. - Duplication of code in tests is not considered an issue as long as the tests cover different aspects of the code. ###Grade Descriptions### **Minimum grade description**: The commit lacks sufficient tests, and changes may break existing functionality. **Maximum grade description**: The commit includes comprehensive tests, validating the new functionality and ensuring existing functionality remains unaffected.",
            "title": "Test Quality",
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
        },
        "triviality": {
            "description": "##Triviality of Commit Changes## ###Evaluation Guidelines### Evaluate whether the commit contains significant or trivial changes. ####Additional Evaluation Conditions#### - Trivial changes do not significantly affect the codebase or introduce new functionality. - Significant changes improve the codebase, fix bugs, or add new features. - Trivial changes may include whitespace changes, typo fixes, or other minor adjustments. ###Grade Descriptions### **Minimum grade description**: The commit is overly trivial, containing insignificant changes. **Maximum grade description**: The commit contains significant, meaningful changes.",
            "title": "Triviality of Commit Changes",
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
        },
    },
    "required": [
        "coding_standards",
        "commit_atomicity",
        "code_quality",
        "message_quality",
        "documentation_quality",
        "codebase_impact",
        "changes_scope",
        "test_quality",
        "triviality",
    ],
}
