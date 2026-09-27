import pytest

from ai_purchase_workflow.composition_root.models import (
    ModelConfigurationError,
    build_purchase_request_model,
)
from ai_purchase_workflow.composition_root.settings import ModelProvider, Settings
from ai_purchase_workflow.infrastructure.models import (
    FakePurchaseRequestModel,
    OpenAICompatiblePurchaseRequestModel,
)


def test_factory_builds_fake_provider_by_default() -> None:
    model = build_purchase_request_model(Settings())

    assert isinstance(model, FakePurchaseRequestModel)


@pytest.mark.parametrize(
    ("provider", "api_key_name", "api_key_value"),
    [
        (ModelProvider.OPENAI, "openai_api_key", "openai-key"),
        (ModelProvider.OPENROUTER, "openrouter_api_key", "router-key"),
    ],
)
def test_factory_builds_external_openai_compatible_provider(
    provider: ModelProvider,
    api_key_name: str,
    api_key_value: str,
) -> None:
    settings = Settings(
        workflow_model_provider=provider,
        workflow_model_name="provider-model",
        **{api_key_name: api_key_value},
    )

    model = build_purchase_request_model(settings)

    assert isinstance(model, OpenAICompatiblePurchaseRequestModel)


def test_factory_builds_ollama_without_external_credentials() -> None:
    model = build_purchase_request_model(
        Settings(workflow_model_provider=ModelProvider.OLLAMA, workflow_model_name="qwen3:8b")
    )

    assert isinstance(model, OpenAICompatiblePurchaseRequestModel)


@pytest.mark.parametrize("provider", [ModelProvider.OPENAI, ModelProvider.OPENROUTER])
def test_factory_requires_external_provider_credentials(provider: ModelProvider) -> None:
    with pytest.raises(ModelConfigurationError, match="API_KEY"):
        build_purchase_request_model(Settings(workflow_model_provider=provider))
