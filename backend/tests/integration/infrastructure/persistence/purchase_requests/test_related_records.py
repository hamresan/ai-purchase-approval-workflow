from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.domain.purchase_requests import (
    ApprovalDecision,
    ApprovalOutcome,
    AuditEntry,
    DraftOrder,
    Money,
    PurchaseItem,
    PurchaseRequest,
    RequestStatus,
)
from ai_purchase_workflow.infrastructure.persistence.models import (
    ApprovalDecisionModel,
    AuditEntryModel,
    DraftOrderModel,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests import (
    SqlAlchemyPurchaseRequestRepository,
)


@pytest.mark.asyncio
async def test_repository_persists_related_business_records(db_session: AsyncSession) -> None:
    item = PurchaseItem("Monitor", 1, Money(Decimal("250.00"), "USD"), "Acme")
    request = PurchaseRequest.create(items=(item,), requester_name="Alex")
    request.draft_order = DraftOrder.create(
        request.id,
        request.items,
        Money(Decimal("250.00"), "USD"),
    )
    request.approval_decision = ApprovalDecision.create(
        request.id,
        ApprovalOutcome.APPROVED,
        "Manager",
        "Approved for test",
    )
    request.audit_entries = (
        AuditEntry.create(request.id, "request_created", "Purchase request created."),
        AuditEntry.create(request.id, "approved", "Purchase request approved."),
    )
    request.transition_to(RequestStatus.PENDING_APPROVAL)
    request.transition_to(RequestStatus.APPROVED)

    repository = SqlAlchemyPurchaseRequestRepository(db_session)
    await repository.add(request)
    loaded = await repository.get(request.id)

    assert loaded is not None
    assert loaded.draft_order == request.draft_order
    assert loaded.approval_decision == request.approval_decision
    assert loaded.audit_entries == request.audit_entries

    assert (
        await db_session.scalar(
            select(DraftOrderModel).where(DraftOrderModel.request_id == request.id)
        )
        is not None
    )
    assert (
        await db_session.scalar(
            select(ApprovalDecisionModel).where(ApprovalDecisionModel.request_id == request.id)
        )
        is not None
    )
    audit_rows = (
        await db_session.scalars(
            select(AuditEntryModel)
            .where(AuditEntryModel.request_id == request.id)
            .order_by(AuditEntryModel.sequence)
        )
    ).all()
    assert [row.sequence for row in audit_rows] == [1, 2]
