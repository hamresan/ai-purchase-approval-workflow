from ai_purchase_workflow.application.purchase_requests.extraction.prompt import (
    PromptTemplateReader,
)


class FakePromptTemplateReader(PromptTemplateReader):
    def __init__(self, template: str = "Schema {schema_version}.") -> None:
        self._template = template
        self.requests: list[tuple[str, str]] = []

    def read(self, name: str, version: str) -> str:
        self.requests.append((name, version))
        return self._template
