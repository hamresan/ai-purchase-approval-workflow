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

        response_format = payload["response_format"]
        assert response_format["type"] == "json_schema"
        assert response_format["json_schema"]["strict"] is True

        schema = response_format["json_schema"]["schema"]
        assert schema["additionalProperties"] is False
        assert schema["properties"]["items"]["items"]["properties"]["quantity"] == {
            "type": "integer",
            "minimum": 1,
        }
        assert schema["properties"]["requester_name"]["type"] == ["string", "null"]
        assert schema["properties"]["review_reason"]["type"] == ["string", "null"]

        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "schema_version": "1.0",
                                    "requester_name": None,
                                    "items": [{"description": "Monitor", "quantity": 1}],
                                    "needs_human_review": False,
                                    "review_reason": None,
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
        "requester_name": None,
        "items": [{"description": "Monitor", "quantity": 1}],
        "needs_human_review": False,
        "review_reason": None,
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
