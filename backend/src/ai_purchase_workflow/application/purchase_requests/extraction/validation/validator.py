from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    ExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.validation.rules import (
    ExtractedRequestValidationRule,
    HumanReviewRule,
    ItemDescriptionRule,
    ItemQuantityRule,
    ItemsPresentRule,
    SchemaVersionRule,
)

DEFAULT_EXTRACTION_VALIDATION_RULES: tuple[ExtractedRequestValidationRule, ...] = (
    SchemaVersionRule(),
    HumanReviewRule(),
    ItemsPresentRule(),
    ItemDescriptionRule(),
    ItemQuantityRule(),
)


class ExtractedRequestValidator:
    def __init__(
        self,
        rules: tuple[ExtractedRequestValidationRule, ...] = DEFAULT_EXTRACTION_VALIDATION_RULES,
    ) -> None:
        self._rules = rules

    def validate(self, extracted: ExtractedPurchaseRequest) -> None:
        for rule in self._rules:
            rule.validate(extracted)
