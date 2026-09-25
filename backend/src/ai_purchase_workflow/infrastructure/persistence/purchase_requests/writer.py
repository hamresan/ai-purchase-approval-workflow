from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest
from ai_purchase_workflow.infrastructure.persistence.models import (
    ApprovalDecisionModel,
    AuditEntryModel,
    DraftOrderModel,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.mapper import (
    PurchaseRequestRelatedRecordMapper,
)


class PurchaseRequestRelatedRecordWriter:
    def __init__(self, mapper: PurchaseRequestRelatedRecordMapper | None = None) -> None:
        self._mapper = mapper or PurchaseRequestRelatedRecordMapper()

    def add_to_session(self, session: AsyncSession, request: PurchaseRequest) -> None:
        if request.draft_order is not None:
            session.add(self._mapper.to_draft_model(request.draft_order))
        if request.approval_decision is not None:
            session.add(self._mapper.to_decision_model(request.approval_decision))
        for sequence, audit in enumerate(request.audit_entries, start=1):
            session.add(self._mapper.to_audit_model(audit, sequence))

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
            session.add(self._mapper.to_draft_model(request.draft_order))
        if request.approval_decision is not None and request.approval_decision.id not in decision_ids:
            session.add(self._mapper.to_decision_model(request.approval_decision))

        new_audits = tuple(audit for audit in request.audit_entries if audit.id not in audit_ids)
        for sequence, audit in enumerate(new_audits, start=len(audit_ids) + 1):
            session.add(self._mapper.to_audit_model(audit, sequence))
