from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ModelRequest:
    system_prompt: str
    user_prompt: str


@dataclass(frozen=True, slots=True)
class ModelResponse:
    content: object


class PurchaseRequestModel(Protocol):
    async def generate(self, request: ModelRequest) -> ModelResponse: ...
