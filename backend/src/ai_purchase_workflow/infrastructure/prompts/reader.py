from importlib.resources import files

from ai_purchase_workflow.application.purchase_requests.extraction.prompt import (
    PromptTemplateReader,
)

_PROMPT_PACKAGE = "ai_purchase_workflow.infrastructure.prompts.templates"


class FilePromptTemplateReader(PromptTemplateReader):
    def read(self, name: str, version: str) -> str:
        resource = files(_PROMPT_PACKAGE).joinpath(name, f"{version}.txt")
        return resource.read_text(encoding="utf-8")
