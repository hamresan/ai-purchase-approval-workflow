import pytest
from pydantic import ValidationError

from ai_purchase_workflow.presentation.purchase_requests.schemas import ApprovalBody


def test_reject_approval_body_requires_reason() -> None:
    with pytest.raises(ValidationError):
        ApprovalBody(action="reject")
