from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest
from ai_purchase_workflow.infrastructure.persistence.models import (
    ApprovalDecisionModel,
    AuditEntryModel,
    DraftOrderModel,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.mapper import (
    PurchaseItemRecordMapper,
)


class PurchaseRequestRelatedRecordWriter:
    def __init__(self, item_mapper: PurchaseItemRecordMapper | None = None) -> None:
        self._item_mapper = item_mapper or PurchaseItemRecordMapper()

    def add_to_session(self, session: AsyncSession, request: PurchaseRequest) -> None:
        if request.draft_order is not None:
            draft = request.draft_order
            session.add(
                DraftOrderModel(
                    id=draft.id,
                    request_id=draft.request_id,
                    items=[self._item_mapper.to_record(item) for item in draft.items],
                    total_amount=draft.total.amount,
                    currency=draft.total.currency,
                    created_at=draft.created_at,
                )
            )
        if request.approval_decision is not None:
            decision = request.approval_decision
            session.add(
                ApprovalDecisionModel(
                    id=decision.id,
                    request_id=decision.request_id,
                    outcome=decision.outcome.value,
                    decided_by=decision.decided_by,
                    reason=decision.reason,
                    decided_at=decision.decided_at,
                )
            )
        for sequence, audit in enumerate(request.audit_entries, start=1):
            session.add(
                AuditEntryModel(
                    id=audit.id,
                    request_id=audit.request_id,
                    sequence=sequence,
                    event_type=audit.event_type,
                    message=audit.message,
                    occurred_at=audit.occurred_at,
                )
            )
