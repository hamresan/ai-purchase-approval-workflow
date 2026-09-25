from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    ExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.validation_rules import (
    ExtractedRequestValidationRule,
)


class ExtractedRequestValidator:
    def __init__(self, rules: tuple[ExtractedRequestValidationRule, ...]) -> None:
        self._rules = rules

    def validate(self, extracted: ExtractedPurchaseRequest) -> None:
        for rule in self._rules:
            rule.validate(extracted)
