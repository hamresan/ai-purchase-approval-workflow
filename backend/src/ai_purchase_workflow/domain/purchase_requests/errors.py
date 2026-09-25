class PurchaseRequestDomainError(Exception):
    """Base error for purchase request domain failures."""


class DomainValidationError(PurchaseRequestDomainError, ValueError):
    """Raised when domain data violates an invariant."""


class InvalidRequestTransitionError(PurchaseRequestDomainError):
    def __init__(self, current_status: str, target_status: str) -> None:
        super().__init__(
            f"Cannot transition purchase request from {current_status} to {target_status}."
        )
