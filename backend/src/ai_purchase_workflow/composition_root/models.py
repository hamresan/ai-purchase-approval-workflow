from ai_purchase_workflow.application.purchase_requests.extraction import (
    ModelResponse,
    PurchaseRequestModel,
)
from ai_purchase_workflow.composition_root.settings import ModelProvider, Settings
from ai_purchase_workflow.infrastructure.models import (
    FakePurchaseRequestModel,
    OpenAICompatibleModelConfig,
    OpenAICompatiblePurchaseRequestModel,
)


class ModelConfigurationError(ValueError):
    """The selected model provider is missing required configuration."""


def build_purchase_request_model(settings: Settings) -> PurchaseRequestModel:
    provider = settings.workflow_model_provider
    if provider is ModelProvider.FAKE:
        return FakePurchaseRequestModel(
            ModelResponse(
                {
                    "schema_version": "1.0",
                    "requester_name": "Dana",
                    "items": [{"description": "Laptop stand", "quantity": 1}],
                }
            )
        )

    base_url, api_key = _provider_connection(settings)
    return OpenAICompatiblePurchaseRequestModel(
        OpenAICompatibleModelConfig(
            base_url=base_url,
            model=settings.workflow_model_name,
            api_key=api_key,
            timeout_seconds=settings.workflow_model_timeout_seconds,
        )
    )


def _provider_connection(settings: Settings) -> tuple[str, str]:
    provider = settings.workflow_model_provider
    if provider is ModelProvider.OLLAMA:
        return settings.workflow_model_base_url or "http://localhost:11434/v1", "ollama"
    if provider is ModelProvider.OPENAI:
        return (
            settings.workflow_model_base_url or "https://api.openai.com/v1",
            _required_key(settings.openai_api_key, "OPENAI_API_KEY"),
        )
    if provider is ModelProvider.OPENROUTER:
        return (
            settings.workflow_model_base_url or "https://openrouter.ai/api/v1",
            _required_key(settings.openrouter_api_key, "OPENROUTER_API_KEY"),
        )
    raise ModelConfigurationError(f"Unsupported model provider: {provider}")


def _required_key(value: str | None, environment_name: str) -> str:
    if value is None or not value.strip():
        raise ModelConfigurationError(f"{environment_name} is required for this model provider.")
    return value
