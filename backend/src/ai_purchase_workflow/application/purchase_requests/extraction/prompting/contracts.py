from typing import Protocol


class PromptTemplateReader(Protocol):
    def read(self, name: str, version: str) -> str: ...
