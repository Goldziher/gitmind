from pathlib import Path

import pytest
from git import Commit

from gitmind.commit_processing.commit import extract_commit_data
from gitmind.configuration_types import MessageDefinition
from gitmind.data_types import CommitMetadata, CommitStatistics
from gitmind.repository import get_commits


@pytest.fixture(scope="session")
def test_commit() -> Commit:
    commits = get_commits(Path(__file__).parent.parent.resolve())
    return next(c for c in commits if c.hexsha == "9c8399e0fe619ff66f8bebe64039fc23a7f107cd")


@pytest.fixture(scope="session")
def commit_data(test_commit: Commit) -> tuple[CommitStatistics, CommitMetadata, str]:
    return extract_commit_data(test_commit)


@pytest.fixture(scope="session")
def describe_commit_message_definitions() -> list[MessageDefinition]:
    return [
        MessageDefinition(
            role="system",
            content="You are an assistant that extracts information and describes the contents of git commits.\n\nEvaluate the provided commit data and provide a detailed description of the changes made in the commit.\n\n- Be precise and concise.\n- Do not use unnecessary superlatives.\n- Do not include any code in the output.\n\nRespond by calling the provided tool 'describe_commit' with a JSON object adhering to its parameter definitions.",
        ),
        MessageDefinition(
            role="user",
            content='**Commit Message**:chore: add e2e testing\n\n**Commit Statistics**:\n- Num Additions: 0\n- Num Copies: 0\n- Num Deletions: 0\n- Num Modifications: 0\n- Num Renames: 0\n- Num Type Changes: 0\n- Num Unmerged: 0\n- Parent Commit Hash: d63b4db42993cd0e5262f79a62c022d09c051eef\n- Total Files Changed: 13\n- Total Lines Changed: 383\n\n**Per file breakdown**:\n{".env":{"deletions":0,"insertions":1,"lines":1},".gitignore":{"deletions":0,"insertions":1,"lines":1},"e2e/__init__.py":{"deletions":0,"insertions":0,"lines":0},"e2e/describe_commit_test.py":{"deletions":0,"insertions":42,"lines":42},"pdm.lock":{"deletions":1,"insertions":12,"lines":13},"pyproject.toml":{"deletions":0,"insertions":6,"lines":6},"src/commit.py":{"deletions":2,"insertions":2,"lines":4},"src/llm/base.py":{"deletions":1,"insertions":1,"lines":2},"src/llm/openai_client.py":{"deletions":18,"insertions":37,"lines":55},"src/llm/result.md":{"deletions":0,"insertions":86,"lines":86},"src/prompts.py":{"deletions":3,"insertions":3,"lines":6},"src/repository.py":{"deletions":6,"insertions":6,"lines":12},"src/types.py":{"deletions":1,"insertions":3,"lines":4},"src/utils/serialization.py":{"deletions":1,"insertions":1,"lines":2}}\n\n**Commit Diff**:\n@@ -1 +0,0 @@\n-OPENAI_API_KEY=sk-proj-3eBo4RLrj7WoNen2rvoMT3BlbkFJWUcHbqZpDusxgHIdEjFb\n\n@@ -2,7 +2,6 @@\n *.log\n *.py[cod]\n .coverage\n-.env\n .mypy_cache/\n .pdm-build/\n .pdm-python\n\n@@ -1,42 +0,0 @@\n-import asyncio\n-from logging import Logger\n-from os import environ\n-from pathlib import Path\n-\n-from dotenv import load_dotenv\n-\n-from src.commit import extract_commit_data\n-from src.llm.openai_client import OpenAIClient, OpenAIOptions\n-from src.prompts import describe_commit_contents\n-from src.repository import get_commits\n-from src.utils.logger import get_logger\n-\n-\n-async def test_describe_commit(logger: Logger) -> None:\n-    """Test the describe_commit_contents function."""\n-    openai_key = environ.get("OPENAI_API_KEY")\n-    assert openai_key is not None, "OPENAI_API_KEY is not set"\n-\n-    client = OpenAIClient(\n-        options=OpenAIOptions(\n-            api_key=openai_key,\n-            model="gpt-4o",\n-        )\n-    )\n-\n-    commits = get_commits(Path(__file__).parent.parent.resolve())\n-    for commit in commits:\n-        logger.info("Describing commit %s", commit.hexsha)\n-        commit_data = extract_commit_data(commit)\n-        description = await describe_commit_contents(client=client, commit_data=commit_data)\n-        logger.info("Description for commit %s: %s", commit.hexsha, description)\n-\n-\n-if __name__ == "__main__":\n-    environ.setdefault("DEBUG_LOGGING", "true")\n-    logger = get_logger(__name__)\n-\n-    load_dotenv()\n-    logger.info("Running test_describe_commit")\n-\n-    asyncio.run(test_describe_commit(logger))\n\n@@ -5,7 +5,7 @@\n groups = ["default", "dev"]\n strategy = ["cross_platform", "inherit_metadata"]\n lock_version = "4.4.1"\n-content_hash = "sha256:d3afd17a9fa9ae05c1693bf78079355e1224bdff7b645a60dd018bb9af3157bb"\n+content_hash = "sha256:7a1a04698bd63123faae11bce6302762b9879ad2bc0185544150ebf2dbb28bb6"\n \n [[package]]\n name = "aiosqlite"\n@@ -798,17 +798,6 @@ files = [\n     {file = "pytest_asyncio-0.23.7.tar.gz", hash = "sha256:5f5c72948f4c49e7db4f29f2521d4031f1c27f86e57b046126654083d4770268"},\n ]\n \n-[[package]]\n-name = "python-dotenv"\n-version = "1.0.1"\n-requires_python = ">=3.8"\n-summary = "Read key-value pairs from a .env file and set them as environment variables"\n-groups = ["default"]\n-files = [\n-    {file = "python-dotenv-1.0.1.tar.gz", hash = "sha256:e324ee90a023d808f1959c46bcbc04446a10ced277783dc6ee09987c37ec10ca"},\n-    {file = "python_dotenv-1.0.1-py3-none-any.whl", hash = "sha256:f7b63ef50f1b690dddf550d03497b66d609393b40b564ed0d674909a68ebf16a"},\n-]\n-\n [[package]]\n name = "python-magic"\n version = "0.4.27"\n\n@@ -17,7 +17,6 @@ dependencies = [\n     "msgspec>=0.18.6",\n     "python-magic>=0.4.27",\n     "jsonschema>=4.22.0",\n-    "python-dotenv>=1.0.1",\n ]\n requires-python = "==3.12.*"\n readme = "README.md"\n@@ -110,11 +109,6 @@ src = ["src", "tests"]\n     "TCH",\n     "TRY",\n ]\n-"e2e/**/*.*" = [\n-    "S101"\n-]\n-\n-\n \n [tool.ruff.format]\n docstring-code-format = true\n\n@@ -4,7 +4,7 @@ from typing import TYPE_CHECKING\n from git import Blob, Commit\n from magic import Magic\n \n-from src.prompts import describe_commit_contents, grade_commit\n+from prompts import describe_commit_contents, grade_commit\n from src.types import CommitDataDTO, ParsedCommitDTO\n \n if TYPE_CHECKING:\n@@ -76,7 +76,7 @@ def extract_commit_data(commit: Commit) -> CommitDataDTO:\n     return CommitDataDTO(\n         total_files_changed=len(diff_list),\n         total_lines_changed=sum(len(diff.splitlines()) for diff in diff_list),\n-        per_files_changes=dict(commit.stats.files),\n+        per_files_changes={change.a_path: change for change in changes},\n         author_email=commit.author.email,\n         author_name=commit.author.name,\n         diff_contents="".join(diff_list),\n\n@@ -19,7 +19,7 @@ class LLMClient(ABC, Generic[ClientConfig]):\n     """Base class for LLM clients."""\n \n     @abstractmethod\n-    def __init__(self, *, config: ClientConfig) -> None:  # pragma: no cover\n+    async def init(self, *, config: ClientConfig) -> None:  # pragma: no cover\n         """Initialize the client.\n \n         Args:\n\n@@ -1,34 +1,25 @@\n-import logging\n from collections.abc import Mapping\n-from typing import TYPE_CHECKING, Union\n+from typing import TYPE_CHECKING, Union, cast\n \n-from httpx import URL\n-from openai import DEFAULT_MAX_RETRIES, NOT_GIVEN, NotGiven, OpenAIError\n+from httpx import URL, Timeout\n+from openai import DEFAULT_MAX_RETRIES, NOT_GIVEN, NotGiven\n from openai.lib.azure import AsyncAzureADTokenProvider\n from openai.types import ChatModel\n-from openai.types.chat import (\n-    ChatCompletionMessageParam,\n-    ChatCompletionSystemMessageParam,\n-    ChatCompletionUserMessageParam,\n-)\n+from openai.types.chat import ChatCompletionMessageParam\n from openai.types.chat.completion_create_params import ResponseFormat\n-from pydantic import BaseModel, ConfigDict\n+from pydantic import BaseModel\n \n-from src.exceptions import LLMClientError\n-from src.llm.base import LLMClient, Message\n+from exceptions import LLMClientError\n+from llm.base import LLMClient, Message\n \n if TYPE_CHECKING:\n     from openai import AsyncClient\n     from openai.lib.azure import AsyncAzureOpenAI\n \n-logger = logging.getLogger(__name__)\n-\n \n class BaseOptions(BaseModel):\n     """Base options for OpenAI clients."""\n \n-    model_config = ConfigDict(arbitrary_types_allowed=True)\n-\n     api_key: str\n     """The API key for the OpenAI model."""\n     model: ChatModel = "gpt-4o"\n@@ -37,7 +28,7 @@ class BaseOptions(BaseModel):\n     """An organization namespace. Note: an error will be raised if this is not configured in the remote API."""\n     project: str | None = None\n     """The project namespace. Note: an error will be raised if this is not configured in the remote API"""\n-    timeout: float | None | NotGiven = NOT_GIVEN\n+    timeout: float | Timeout | None | NotGiven = NOT_GIVEN\n     """The timeout for the HTTPX client."""\n     max_retries: int = DEFAULT_MAX_RETRIES\n     """The maximum number of retries for the HTTPX client."""\n@@ -130,25 +121,15 @@ class OpenAIClient(LLMClient[AzureOpenAIOptions | OpenAIOptions]):\n         Returns:\n             The completion generated by the client.\n         """\n-        try:\n-            result = await self._client.chat.completions.create(\n-                model=self._model,\n-                messages=self._map_messages_to_openai_message_types(messages),\n-                response_format=ResponseFormat(type="json_object" if json_response else "text"),\n-                stream=True,\n-            )\n-            content = ""\n-            async for chunk in result:\n-                if delta := chunk.choices[0].delta.content:\n-                    logger.info("%s", delta)\n-                    content += delta\n-\n-            if not content:\n-                raise LLMClientError("Failed to generate completion")\n+        result = await self._client.chat.completions.create(\n+            model=self._model,\n+            messages=self._map_messages_to_openai_message_types(messages),\n+            response_format=ResponseFormat(type="json_object" if json_response else "text"),\n+        )\n+        if result.choices and (content := result.choices[0].message.content):\n+            return cast(str, content)\n \n-            return content\n-        except OpenAIError as e:\n-            raise LLMClientError("Failed to generate completion") from e\n+        raise LLMClientError("Failed to generate completion")\n \n     @staticmethod\n     def _map_messages_to_openai_message_types(messages: list[Message]) -> list[ChatCompletionMessageParam]:\n@@ -165,14 +146,14 @@ class OpenAIClient(LLMClient[AzureOpenAIOptions | OpenAIOptions]):\n             match message["role"]:\n                 case "system":\n                     result.append(\n-                        ChatCompletionSystemMessageParam(\n+                        ChatCompletionMessageParam(\n                             role="system",\n                             content=message["content"],\n                         )\n                     )\n                 case "user":\n                     result.append(\n-                        ChatCompletionUserMessageParam(\n+                        ChatCompletionMessageParam(\n                             role="user",\n                             content=message["content"],\n                         )\n\n@@ -1,86 +0,0 @@\n-Description for commit d63b4db42993cd0e5262f79a62c022d09c051eef: The commit involves substantial changes across multiple\n-files with a focus on restructuring the codebase and cleaning up unnecessary files. Here\'s a detailed breakdown of the\n-modifications:\n-\n-### Overview of Changes:\n-\n-- **Total Files Changed**: 8\n-- **Total Lines Changed**: 8\n-- **Additions**: 0\n-- **Deletions**: 0\n-- **Copies**: 0\n-- **Modifications**: 0\n-- **Renames**: 0\n-- **Type Changes**: 0\n-\n-### Detailed Breakdown by File:\n-\n-1. **`.pre-commit-config.yaml`**:\n-    - **Changes**: 2 lines modified.\n-    - **Details**:\n-        - The `rev` for `ruff-pre-commit` was reverted from `v0.4.8` to `v0.4.7`.\n-\n-2. **`src/client.py`**:\n-    - **Changes**: 273 lines removed.\n-    - **Details**:\n-        - The entirety of `src/client.py` was removed. This file contained several classes and methods related to\n-          wrapping OpenAI models, including `OpenAIClient`, various utility functions, and types.\n-\n-3. **`src/commit.py`**:\n-    - **Changes**: 13 lines modified (7 insertions, 6 deletions).\n-    - **Details**:\n-        - The `parse_commit_contents` function\'s definitions were updated to replace `LLMClient` with `OpenAIClient`.\n-        - Calls to `describe_commit_contents` and `grade_commit` were updated to be methods of the `OpenAIClient`\n-          instance rather than standalone functions.\n-\n-4. **`src/exceptions.py`**:\n-    - **Changes**: 11 lines added.\n-    - **Details**:\n-        - Added new class `LLMClientError` as a base class for errors in the LLM module.\n-\n-5. **`src/llm/__init__.py`**:\n-    - **Changes**: No changes.\n-\n-6. **`src/llm/base.py`**:\n-    - **Changes**: 46 lines added.\n-    - **Details**:\n-        - Added an abstract base class `LLMClient` and associated types and methods.\n-        - Defined `Message` type and `LLMClient` class with abstract methods to initialize the client and create\n-          completions asynchronously.\n-\n-7. **`src/llm/openai_client.py`**:\n-    - **Changes**: 163 lines added.\n-    - **Details**:\n-        - Added a new `OpenAIClient` class with methods for describing commit contents and grading commits.\n-        - The `OpenAIClient` class wraps OpenAI models, provides singleton pattern methods, and handles OpenAI client\n-          initialization and requests.\n-\n-8. **`src/prompts.py`**:\n-    - **Changes**: 187 lines added.\n-    - **Details**:\n-        - Added methods `describe_commit_contents` and `grade_commit`. These methods create prompts for OpenAI models to\n-          generate descriptions and grades for git commits.\n-        - Both functions log the prompts and handle the communication with the OpenAI API, with appropriate error\n-          handling.\n-\n-### Key Objectives of the Commit:\n-\n-1. **Refactoring**:\n-    - The commit involved refactoring code to clean up and streamline functionality, especially around the use of OpenAI\n-      clients.\n-\n-2. **Modularization**:\n-    - The OpenAI-related utilities were modularized into new files (`src/llm/base.py` and `src/llm/openai_client.py`),\n-      separating concerns more cleanly.\n-\n-3. **Error Handling**:\n-    - Enhanced error handling with new exception classes specifically for the LLM module.\n-\n-4. **Consistency**:\n-    - Ensured that the appropriate client (`OpenAIClient`) is used consistently across the codebase.\n-\n-### Conclusion:\n-\n-This commit significantly restructured the handling of OpenAI functionalities, improved modularity by segregating base\n-class definitions and specific client implementations, and cleaned up outdated or redundant code. This should improve\n-the maintainability and readability of the codebase.\n\n@@ -3,12 +3,12 @@ from typing import TYPE_CHECKING, Any\n \n from msgspec import DecodeError\n \n-from src.exceptions import CriticError, LLMClientError\n-from src.llm.base import LLMClient, Message\n+from exceptions import CriticError, LLMClientError\n+from llm.base import LLMClient, Message\n from src.rules import DEFAULT_GRADING_RULES\n from src.types import CommitDataDTO, CommitGradingResult, Rule\n-from src.utils.logger import get_logger\n from src.utils.serialization import deserialize, serialize\n+from utils.logger import get_logger\n \n logger = get_logger(__name__)\n \n\n@@ -1,21 +1,21 @@\n-from git import Commit, PathLike, Repo\n+from git import Commit, Repo\n \n \n-def clone_repository(repo_path: PathLike, branch_name: str, target_path: PathLike) -> Repo:\n+def clone_repository(repo_url: str, branch_name: str, repo_path: str) -> Repo:\n     """Clone a Git repository.\n \n     Args:\n-        repo_path: The URL or path of the Git repository.\n+        repo_url: The URL of the Git repository.\n         branch_name: The name of the branch to clone.\n-        target_path: The path to clone the repository to.\n+        repo_path: The path to clone the repository to.\n \n     Returns:\n         The cloned Git repository.\n     """\n-    return Repo.clone_from(url=repo_path, to_path=target_path, branch=branch_name)\n+    return Repo.clone_from(repo_url, repo_path, branch=branch_name)\n \n \n-def get_commits(repo_path: PathLike) -> list[Commit]:\n+def get_commits(repo_path: str) -> list[Commit]:\n     """Get the commits of a Git repository.\n \n     Args:\n\n@@ -1,7 +1,5 @@\n from typing import TYPE_CHECKING, TypedDict\n \n-from git.types import PathLike\n-\n if TYPE_CHECKING:\n     from git.types import Files_TD\n \n@@ -30,7 +28,7 @@ class CommitDataDTO(TypedDict):\n     """The total number of files changed in the commit."""\n     total_lines_changed: int\n     """The total number of lines changed in the commit."""\n-    per_files_changes: dict[str | PathLike, "Files_TD"]\n+    per_files_changes: dict[str, "Files_TD"]\n     """The changes per file in the commit."""\n     author_email: str | None\n     """The email of the author of the commit."""\n\n@@ -35,4 +35,4 @@ def serialize(value: Any) -> bytes:\n     Raises:\n         EncodeError: If error encoding ``value``.\n     """\n-    return encode(value)\n+    return encode(value, order="sorted")\n',
        ),
    ]
