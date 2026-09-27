import json

import httpx
import pytest

from ai_purchase_workflow.application.purchase_requests.extraction import ModelRequest
from ai_purchase_workflow.application.purchase_requests.extraction.errors import (
    ModelUnavailableError,
)
from ai_purchase_workflow.infrastructure.models import (
    OpenAICompatibleModelConfig,
    OpenAICompatiblePurchaseRequestModel,
)


def build_model(handler: httpx.AsyncBaseTransport) -> OpenAICompatiblePurchaseRequestModel:
    return OpenAICompatiblePurchaseRequestModel(
        OpenAICompatibleModelConfig(
            base_url="https://model.example/v1",
            model="example-model",
            api_key="secret",
            timeout_seconds=5.0,
        ),
        transport=handler,
    )


@pytest.mark.asyncio
async def test_generate_maps_openai_compatible_json_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer secret"
        payload = json.loads(request.content)
        assert payload["model"] == "example-model"
        assert payload["response_format"] == {"type": "json_object"}
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "schema_version": "1.0",
                                    "items": [{"description": "Monitor", "quantity": 1}],
                                }
                            )
                        }
                    }
                ]
            },
        )

    model = build_model(httpx.MockTransport(handler))
    response = await model.generate(ModelRequest("system", "user"))

    assert response.content == {
        "schema_version": "1.0",
        "items": [{"description": "Monitor", "quantity": 1}],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [401, 429, 500])
async def test_generate_maps_provider_http_errors_safely(status_code: int) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"error": {"message": "provider detail"}})

    model = build_model(httpx.MockTransport(handler))

    with pytest.raises(ModelUnavailableError, match="invalid response"):
        await model.generate(ModelRequest("system", "user"))


@pytest.mark.asyncio
async def test_generate_rejects_malformed_provider_payload() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []})

    model = build_model(httpx.MockTransport(handler))

    with pytest.raises(ModelUnavailableError, match="invalid response"):
        await model.generate(ModelRequest("system", "user"))


@pytest.mark.asyncio
async def test_generate_maps_timeout_to_safe_provider_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    model = build_model(httpx.MockTransport(handler))

    with pytest.raises(ModelUnavailableError, match="temporarily unavailable"):
        await model.generate(ModelRequest("system", "user"))
