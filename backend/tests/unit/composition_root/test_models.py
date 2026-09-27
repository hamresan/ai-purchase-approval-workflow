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
    "settings",
    [
        Settings(
            workflow_model_provider=ModelProvider.OPENAI,
            workflow_model_name="provider-model",
            openai_api_key="openai-key",
        ),
        Settings(
            workflow_model_provider=ModelProvider.OPENROUTER,
            workflow_model_name="provider-model",
            openrouter_api_key="router-key",
        ),
    ],
)
def test_factory_builds_external_openai_compatible_provider(settings: Settings) -> None:
    model = build_purchase_request_model(settings)

    assert isinstance(model, OpenAICompatiblePurchaseRequestModel)


def test_factory_builds_ollama_without_external_credentials() -> None:
    model = build_purchase_request_model(
        Settings(workflow_model_provider=ModelProvider.OLLAMA, workflow_model_name="qwen3:8b")
    )

    assert isinstance(model, OpenAICompatiblePurchaseRequestModel)


@pytest.mark.parametrize("provider", [ModelProvider.OPENAI, ModelProvider.OPENROUTER])
def test_factory_requires_external_provider_credentials(
    provider: ModelProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    settings = Settings(
        workflow_model_provider=provider,
        openai_api_key=None,
        openrouter_api_key=None,
    )

    with pytest.raises(ModelConfigurationError, match="API_KEY"):
        build_purchase_request_model(settings)
