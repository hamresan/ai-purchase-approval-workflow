from ai_purchase_workflow.application.purchase_requests.extraction import (
    ModelRequest,
    ModelResponse,
    PurchaseRequestModel,
)
from ai_purchase_workflow.application.purchase_requests.extraction.errors import ModelUnavailableError


class UnavailablePurchaseRequestModel(PurchaseRequestModel):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        del request
        raise ModelUnavailableError("Model provider is temporarily unavailable.")
