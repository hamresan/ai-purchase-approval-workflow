from dataclasses import dataclass
from enum import StrEnum


class ApprovalAction(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"


@dataclass(frozen=True, slots=True)
class EditPurchaseItem:
    description: str
    quantity: int
