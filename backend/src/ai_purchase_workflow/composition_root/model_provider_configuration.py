from dataclasses import dataclass

from ai_purchase_workflow.composition_root.settings import ModelProvider, Settings


class ModelConfigurationError(ValueError):
    """The selected model provider is missing required configuration."""


@dataclass(frozen=True, slots=True)
class ModelProviderConnection:
    base_url: str
    api_key: str


class ModelProviderConfigurationResolver:
    def resolve(self, settings: Settings) -> ModelProviderConnection:
        provider = settings.workflow_model_provider
        if provider is ModelProvider.OLLAMA:
            return ModelProviderConnection(
                settings.workflow_model_base_url or "http://localhost:11434/v1",
                "ollama",
            )
        if provider is ModelProvider.OPENAI:
            return ModelProviderConnection(
                settings.workflow_model_base_url or "https://api.openai.com/v1",
                self.require_key(settings.openai_api_key, "OPENAI_API_KEY"),
            )
        if provider is ModelProvider.OPENROUTER:
            return ModelProviderConnection(
                settings.workflow_model_base_url or "https://openrouter.ai/api/v1",
                self.require_key(settings.openrouter_api_key, "OPENROUTER_API_KEY"),
            )
        raise ModelConfigurationError(f"Unsupported model provider: {provider}")

    @staticmethod
    def require_key(value: str | None, environment_name: str) -> str:
        if value is None or not value.strip():
            raise ModelConfigurationError(
                f"{environment_name} is required for this model provider."
            )
        return value
