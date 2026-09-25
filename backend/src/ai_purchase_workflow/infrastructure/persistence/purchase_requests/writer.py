from sqlalchemy import select
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

    async def add_missing_to_session(
        self,
        session: AsyncSession,
        request: PurchaseRequest,
    ) -> None:
        draft_ids = set(
            (
                await session.scalars(
                    select(DraftOrderModel.id).where(DraftOrderModel.request_id == request.id)
                )
            ).all()
        )
        decision_ids = set(
            (
                await session.scalars(
                    select(ApprovalDecisionModel.id).where(
                        ApprovalDecisionModel.request_id == request.id
                    )
                )
            ).all()
        )
        audit_ids = set(
            (
                await session.scalars(
                    select(AuditEntryModel.id).where(AuditEntryModel.request_id == request.id)
                )
            ).all()
        )
        if request.draft_order is not None and request.draft_order.id not in draft_ids:
            self._add_draft(session, request)
        if request.approval_decision is not None and request.approval_decision.id not in decision_ids:
            self._add_decision(session, request)
        new_audits = tuple(audit for audit in request.audit_entries if audit.id not in audit_ids)
        self._add_audits(session, request, new_audits, start_sequence=len(audit_ids) + 1)

    def add_to_session(self, session: AsyncSession, request: PurchaseRequest) -> None:
        self._add_draft(session, request)
        self._add_decision(session, request)
        self._add_audits(session, request, request.audit_entries, start_sequence=1)

    def _add_draft(self, session: AsyncSession, request: PurchaseRequest) -> None:
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
    def _add_decision(self, session: AsyncSession, request: PurchaseRequest) -> None:
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
    @staticmethod
    def _add_audits(
        session: AsyncSession,
        request: PurchaseRequest,
        audits: tuple,
        start_sequence: int,
    ) -> None:
        for sequence, audit in enumerate(audits, start=start_sequence):
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
