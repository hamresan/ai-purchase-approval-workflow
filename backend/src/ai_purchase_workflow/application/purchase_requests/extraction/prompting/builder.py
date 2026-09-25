from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    EXTRACTED_REQUEST_SCHEMA_VERSION,
    ModelRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.prompting.contracts import (
    PromptTemplateReader,
)

EXTRACTION_PROMPT_NAME = "purchase_request_extraction"
EXTRACTION_PROMPT_VERSION = "v1"


class PurchaseRequestPromptBuilder:
    def __init__(self, reader: PromptTemplateReader) -> None:
        self._reader = reader

    def build(self, free_text: str) -> ModelRequest:
        normalized = free_text.strip()
        if not normalized:
            raise ValueError("Purchase request text must not be empty.")

        template = self._reader.read(EXTRACTION_PROMPT_NAME, EXTRACTION_PROMPT_VERSION)
        system_prompt = template.format(schema_version=EXTRACTED_REQUEST_SCHEMA_VERSION)
        return ModelRequest(system_prompt=system_prompt, user_prompt=normalized)
