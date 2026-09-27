from ai_purchase_workflow.application.purchase_requests.extraction import (
    ModelResponse,
    PurchaseRequestModel,
)
from ai_purchase_workflow.composition_root.model_provider_configuration import (
    ModelConfigurationError,
    ModelProviderConfigurationResolver,
)
from ai_purchase_workflow.composition_root.settings import ModelProvider, Settings
from ai_purchase_workflow.infrastructure.models import (
    FakePurchaseRequestModel,
    OpenAICompatibleModelConfig,
    OpenAICompatiblePurchaseRequestModel,
)

__all__ = ["ModelConfigurationError", "build_purchase_request_model"]


def build_purchase_request_model(settings: Settings) -> PurchaseRequestModel:
    if settings.workflow_model_provider is ModelProvider.FAKE:
        return FakePurchaseRequestModel(
            ModelResponse(
                {
                    "schema_version": "1.0",
                    "requester_name": "Dana",
                    "items": [{"description": "Laptop stand", "quantity": 1}],
                }
            )
        )

    connection = ModelProviderConfigurationResolver().resolve(settings)
    return OpenAICompatiblePurchaseRequestModel(
        OpenAICompatibleModelConfig(
            base_url=connection.base_url,
            model=settings.workflow_model_name,
            api_key=connection.api_key,
            timeout_seconds=settings.workflow_model_timeout_seconds,
        )
    )
