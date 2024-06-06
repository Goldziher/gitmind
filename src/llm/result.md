Description for commit d63b4db42993cd0e5262f79a62c022d09c051eef: The commit involves substantial changes across multiple
files with a focus on restructuring the codebase and cleaning up unnecessary files. Here’s a detailed breakdown of the
modifications:

### Overview of Changes:

- **Total Files Changed**: 8
- **Total Lines Changed**: 8
- **Additions**: 0
- **Deletions**: 0
- **Copies**: 0
- **Modifications**: 0
- **Renames**: 0
- **Type Changes**: 0

### Detailed Breakdown by File:

1. **`.pre-commit-config.yaml`**:
    - **Changes**: 2 lines modified.
    - **Details**:
        - The `rev` for `ruff-pre-commit` was reverted from `v0.4.8` to `v0.4.7`.

2. **`src/client.py`**:
    - **Changes**: 273 lines removed.
    - **Details**:
        - The entirety of `src/client.py` was removed. This file contained several classes and methods related to
          wrapping OpenAI models, including `OpenAIClient`, various utility functions, and types.

3. **`src/commit.py`**:
    - **Changes**: 13 lines modified (7 insertions, 6 deletions).
    - **Details**:
        - The `parse_commit_contents` function’s definitions were updated to replace `LLMClient` with `OpenAIClient`.
        - Calls to `describe_commit_contents` and `grade_commit` were updated to be methods of the `OpenAIClient`
          instance rather than standalone functions.

4. **`src/exceptions.py`**:
    - **Changes**: 11 lines added.
    - **Details**:
        - Added new class `LLMClientError` as a base class for errors in the LLM module.

5. **`src/llm/__init__.py`**:
    - **Changes**: No changes.

6. **`src/llm/base.py`**:
    - **Changes**: 46 lines added.
    - **Details**:
        - Added an abstract base class `LLMClient` and associated types and methods.
        - Defined `Message` type and `LLMClient` class with abstract methods to initialize the client and create
          completions asynchronously.

7. **`src/llm/openai_client.py`**:
    - **Changes**: 163 lines added.
    - **Details**:
        - Added a new `OpenAIClient` class with methods for describing commit contents and grading commits.
        - The `OpenAIClient` class wraps OpenAI models, provides singleton pattern methods, and handles OpenAI client
          initialization and requests.

8. **`src/prompts.py`**:
    - **Changes**: 187 lines added.
    - **Details**:
        - Added methods `describe_commit_contents` and `grade_commit`. These methods create prompts for OpenAI models to
          generate descriptions and grades for git commits.
        - Both functions log the prompts and handle the communication with the OpenAI API, with appropriate error
          handling.

### Key Objectives of the Commit:

1. **Refactoring**:
    - The commit involved refactoring code to clean up and streamline functionality, especially around the use of OpenAI
      clients.

2. **Modularization**:
    - The OpenAI-related utilities were modularized into new files (`src/llm/base.py` and `src/llm/openai_client.py`),
      separating concerns more cleanly.

3. **Error Handling**:
    - Enhanced error handling with new exception classes specifically for the LLM module.

4. **Consistency**:
    - Ensured that the appropriate client (`OpenAIClient`) is used consistently across the codebase.

### Conclusion:

This commit significantly restructured the handling of OpenAI functionalities, improved modularity by segregating base
class definitions and specific client implementations, and cleaned up outdated or redundant code. This should improve
the maintainability and readability of the codebase.
