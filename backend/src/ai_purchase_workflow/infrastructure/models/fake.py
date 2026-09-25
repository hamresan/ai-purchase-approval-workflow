from ai_purchase_workflow.application.purchase_requests.extraction import (
    ModelRequest,
    ModelResponse,
    PurchaseRequestModel,
)


class FakePurchaseRequestModel(PurchaseRequestModel):
    def __init__(self, response: ModelResponse) -> None:
        self._response = response
        self.requests: list[ModelRequest] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        return self._response
