from pathlib import Path
from re import Pattern
from re import compile as compile_regex
from typing import Annotated, Any, Final, Literal

from pydantic import DirectoryPath, Field, SecretStr, field_validator, model_validator
from pydantic_core import Url
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)

CONFIG_FILE_NAME: Final[str] = "gitmind-config"

git_regex: Pattern[str] = compile_regex(r"((git|ssh|http(s)?)|(git@[\w\.-]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?")


class BaseGitmineSetting(BaseSettings):
    """Base settings for GitMine."""


SupportedProviders = Literal["openai", "azure-openai", "groq"]
Verbosity = Literal["silent", "standard", "verbose", "debug"]
CacheType = Literal["memory", "file"]


class GitMindSettings(BaseGitmineSetting):
    """Configuration for the GitMind Application."""

    model_config = SettingsConfigDict(
        arbitrary_types_allowed=True,
        regex_engine="python-re",
        env_prefix="GITMIND_",
        env_file=".env",
        json_file=f"{CONFIG_FILE_NAME}.json",
        pyproject_toml_table_header=("tool", "gitmind"),
        toml_file=f"{CONFIG_FILE_NAME}.toml",
        yaml_file=[f"{CONFIG_FILE_NAME}.yaml", f"{CONFIG_FILE_NAME}.yml"],
        extra="allow",
    )

    cache_type: Annotated[CacheType, Field(description="The cache type to use.")] = "memory"
    target_repo: Annotated[
        DirectoryPath | Annotated[str, Field(pattern=git_regex)] | None,
        Field(description="The target repository. The value can be either a URL or a directory path."),
    ] = None
    mode: Annotated[
        Verbosity, Field(description="The output level of the gitmind CLI mode to run the application.")
    ] = "standard"
    max_request_retries: Annotated[int, Field(description="The maximum number of retries for requests.")] = 0
    provider_name: Annotated[SupportedProviders, Field(description="The name of the LLM provider")]
    provider_api_key: Annotated[SecretStr, Field(description="The API key for the provider")]
    provider_model: Annotated[str, Field(description="The model to use for completions.")]
    provider_endpoint_url: Annotated[
        Url | None,
        Field(description="The endpoint for the provider API."),
    ] = None
    provider_deployment_id: Annotated[str | None, Field(description="The deployment for the provider API")] = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise the settings sources for the GitMindSettings class to load multiple setting types.

        See: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources
        """
        return (
            init_settings,
            JsonConfigSettingsSource(settings_cls),
            YamlConfigSettingsSource(settings_cls),
            TomlConfigSettingsSource(settings_cls),
            PyprojectTomlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    @field_validator("target_repo", mode="after")
    @classmethod
    def validate_target_repo(cls, value: str | Path | None) -> str | Path:
        """Validate the target repository value.

        Args:
            value (str | DirectoryPath | None): The target repository value.

        Returns:
            str | DirectoryPath | None: The validated target repository value.
        """
        if value is None:
            cwd = Path.cwd()
            if not cwd.joinpath(".git").exists():
                raise ValueError("The current directory is not a git repository.")
            return cwd
        if isinstance(value, Path) and not value.joinpath(".git").exists():
            raise ValueError("The target_repo directory is not a git repository.")

        return value

    @model_validator(mode="before")
    @classmethod
    def validate_values(cls, values_dict: dict[str, Any]) -> dict[str, Any]:
        """Validate the values of the settings.

        Args:
            values_dict (dict[str, Any]): The values dictionary.

        Raises:
            ValidationError: If the values are invalid.

        Returns:
            dict[str, Any]: The validated values dictionary.
        """
        if provider_name := values_dict.get("provider_name"):
            if provider_name == "azure-openai":
                missing_fields = []
                if not values_dict.get("provider_endpoint_url"):
                    missing_fields.append("provider_endpoint_url")
                if not values_dict.get("provider_deployment_id"):
                    missing_fields.append("provider_deployment_id")
                if missing_fields:
                    raise ValueError(f"Missing required parameters: {', '.join(missing_fields)}")
            return values_dict

        raise ValueError("Missing required parameter: provider_name")
