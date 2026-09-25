import pytest

from ai_purchase_workflow.application.purchase_requests.extraction import (
    ModelRequest,
    ModelResponse,
)
from ai_purchase_workflow.infrastructure.models import FakePurchaseRequestModel


@pytest.mark.asyncio
async def test_generate_returns_configured_response_and_records_request() -> None:
    response = ModelResponse(content={"schema_version": "1.0", "items": []})
    model = FakePurchaseRequestModel(response)
    request = ModelRequest(system_prompt="system", user_prompt="user")

    result = await model.generate(request)

    assert result is response
    assert model.requests == [request]
