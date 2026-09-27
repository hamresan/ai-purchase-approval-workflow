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
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()
                payload = response.json()
                content = payload["choices"][0]["message"]["content"]
                if not isinstance(content, str):
                    raise ModelUnavailableError("Model provider returned an invalid response.")
                return ModelResponse(json.loads(content))
        except ModelUnavailableError:
            raise
        except (httpx.TimeoutException, httpx.RequestError) as error:
            raise ModelUnavailableError("Model provider is temporarily unavailable.") from error
        except (httpx.HTTPStatusError, json.JSONDecodeError, KeyError, IndexError, TypeError) as error:
            raise ModelUnavailableError("Model provider returned an invalid response.") from error
