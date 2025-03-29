from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Annotated, Any, Final, Literal

from pydantic import DirectoryPath, Field, SecretStr, field_validator, model_validator
from pydantic_core import Url  # noqa: TC002
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)

from gitmind.llm.base import LLMClient  # noqa: TC001

CONFIG_FILE_NAME: Final[str] = "gitmind-config"


SupportedProviders = Literal["openai", "azure-openai", "groq"]
Verbosity = Literal["silent", "standard", "verbose", "debug"]
CacheType = Literal["memory", "file"]


class GitMindSettings(BaseSettings):
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
        DirectoryPath | str | None,
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
            value: The target repository value.

        Raises:
            ValueError: If the target repository is not a git repository.

        Returns:
            The validated target repository value.
        """
        if value is None:
            value = Path.cwd()

        if isinstance(value, Path) and not value.joinpath(".git").exists():
            raise ValueError(f"The value for target_repo - {value} - is not a git repository.")

        return value

    @model_validator(mode="before")
    @classmethod
    def validate_values(cls, values_dict: dict[str, Any]) -> dict[str, Any]:
        """Validate the values of the settings.

        Args:
            values_dict: The values dictionary.

        Raises:
            ValueError: If the values are invalid.

        Returns:
            The validated values dictionary.
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

    @cached_property
    def llm_client(self) -> LLMClient:
        """Get the LLM client for the provider.

        Returns:
            The LLM client for the provider.
        """
        if self.provider_name == "azure-openai":
            from gitmind.llm.openai_client import OpenAIClient

            return OpenAIClient(
                api_key=self.provider_api_key.get_secret_value(),
                model_name=self.provider_model,
                endpoint_url=self.provider_endpoint_url,  # type: ignore[arg-type]
                deployment_id=self.provider_deployment_id,
            )
        if self.provider_name == "groq":
            from gitmind.llm.groq_client import GroqClient

            return GroqClient(
                api_key=self.provider_api_key.get_secret_value(),
                model_name=self.provider_model,
                endpoint_url=self.provider_endpoint_url,  # type: ignore[arg-type]
            )

        from gitmind.llm.openai_client import OpenAIClient

        return OpenAIClient(
            api_key=self.provider_api_key.get_secret_value(),
            model_name=self.provider_model,
            endpoint_url=self.provider_endpoint_url,  # type: ignore[arg-type]
        )
