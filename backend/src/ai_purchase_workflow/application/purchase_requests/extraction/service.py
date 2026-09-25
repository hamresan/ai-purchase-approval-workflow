from dataclasses import dataclass

from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    ExtractedPurchaseRequest,
    PurchaseRequestModel,
)
from ai_purchase_workflow.application.purchase_requests.extraction.errors import ExtractionError
from ai_purchase_workflow.application.purchase_requests.extraction.mapper import (
    StructuredOutputMapper,
)
from ai_purchase_workflow.application.purchase_requests.extraction.prompt import (
    PurchaseRequestPromptBuilder,
)
from ai_purchase_workflow.application.purchase_requests.extraction.validator import (
    ExtractedRequestValidator,
)


@dataclass(frozen=True, slots=True)
class ExtractionOutcome:
    extracted_request: ExtractedPurchaseRequest | None
    needs_human_review: bool
    review_reason: str | None

    @classmethod
    def success(cls, extracted_request: ExtractedPurchaseRequest) -> "ExtractionOutcome":
        return cls(extracted_request, False, None)

    @classmethod
    def human_review(cls, reason: str) -> "ExtractionOutcome":
        return cls(None, True, reason)


class ExtractPurchaseRequest:
    def __init__(
        self,
        model: PurchaseRequestModel,
        prompt_builder: PurchaseRequestPromptBuilder,
        mapper: StructuredOutputMapper,
        validator: ExtractedRequestValidator,
    ) -> None:
        self._model = model
        self._prompt_builder = prompt_builder
        self._mapper = mapper
        self._validator = validator

    async def execute(self, free_text: str) -> ExtractionOutcome:
        request = self._prompt_builder.build(free_text)
        response = await self._model.generate(request)
        try:
            extracted = self._mapper.map(response)
            self._validator.validate(extracted)
        except ExtractionError as error:
            return ExtractionOutcome.human_review(str(error))
        return ExtractionOutcome.success(extracted)
