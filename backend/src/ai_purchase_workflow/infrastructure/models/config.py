from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpenAICompatibleModelConfig:
    base_url: str
    model: str
    api_key: str
    timeout_seconds: float
