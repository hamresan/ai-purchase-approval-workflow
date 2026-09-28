import json

import httpx

from ai_purchase_workflow.application.purchase_requests.extraction import (
    ModelRequest,
    ModelResponse,
    PurchaseRequestModel,
)
from ai_purchase_workflow.application.purchase_requests.extraction.errors import (
    ModelUnavailableError,
)
from ai_purchase_workflow.infrastructure.models.config import OpenAICompatibleModelConfig
from ai_purchase_workflow.infrastructure.models.responses import ChatCompletionResponse

_PURCHASE_REQUEST_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "purchase_request_extraction",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "schema_version": {"type": "string", "const": "1.0"},
                "requester_name": {"type": ["string", "null"]},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "minLength": 1},
                            "quantity": {"type": "integer", "minimum": 1},
                        },
                        "required": ["description", "quantity"],
                        "additionalProperties": False,
                    },
                },
                "needs_human_review": {"type": "boolean"},
                "review_reason": {"type": ["string", "null"]},
            },
            "required": [
                "schema_version",
                "requester_name",
                "items",
                "needs_human_review",
                "review_reason",
            ],
            "additionalProperties": False,
        },
    },
}


class OpenAICompatiblePurchaseRequestModel(PurchaseRequestModel):
    def __init__(
        self,
        config: OpenAICompatibleModelConfig,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport

    async def generate(self, request: ModelRequest) -> ModelResponse:
        try:
            async with httpx.AsyncClient(
                base_url=self._config.base_url,
                timeout=self._config.timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    "/chat/completions",
                    headers={"Authorization": f"Bearer {self._config.api_key}"},
                    json={
                        "model": self._config.model,
                        "messages": [
                            {"role": "system", "content": request.system_prompt},
                            {"role": "user", "content": request.user_prompt},
                        ],
                        "response_format": _PURCHASE_REQUEST_RESPONSE_FORMAT,
                    },
                )
                response.raise_for_status()
                payload = ChatCompletionResponse.model_validate_json(response.content)
                if not payload.choices:
                    raise ModelUnavailableError("Model provider returned an invalid response.")
                return ModelResponse(json.loads(payload.choices[0].message.content))
        except ModelUnavailableError:
            raise
        except (httpx.TimeoutException, httpx.RequestError) as error:
            raise ModelUnavailableError("Model provider is temporarily unavailable.") from error
        except (httpx.HTTPStatusError, json.JSONDecodeError, ValueError) as error:
            raise ModelUnavailableError("Model provider returned an invalid response.") from error
