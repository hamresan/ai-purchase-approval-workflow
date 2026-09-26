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


class DraftOrderSynchronizer:
    def __init__(self, mapper: PurchaseRequestRelatedRecordMapper) -> None:
        self._mapper = mapper

    async def sync(self, session: AsyncSession, request: PurchaseRequest) -> None:
        if request.draft_order is None:
            return
        model = await session.scalar(
            select(DraftOrderModel).where(DraftOrderModel.request_id == request.id)
        )
        if model is None:
            session.add(self._mapper.to_draft_model(request.draft_order))
            return
        self._mapper.update_draft_model(model, request.draft_order)


class ApprovalDecisionSynchronizer:
    def __init__(self, mapper: PurchaseRequestRelatedRecordMapper) -> None:
        self._mapper = mapper

    async def sync(self, session: AsyncSession, request: PurchaseRequest) -> None:
        if request.approval_decision is None:
            return
        exists = await session.scalar(
            select(ApprovalDecisionModel.id).where(
                ApprovalDecisionModel.id == request.approval_decision.id
            )
        )
        if exists is None:
            session.add(self._mapper.to_decision_model(request.approval_decision))


class AuditEntrySynchronizer:
    def __init__(self, mapper: PurchaseRequestRelatedRecordMapper) -> None:
        self._mapper = mapper

    async def sync(self, session: AsyncSession, request: PurchaseRequest) -> None:
        audit_ids = set(
            (
                await session.scalars(
                    select(AuditEntryModel.id).where(AuditEntryModel.request_id == request.id)
                )
            ).all()
        )
        new_audits = tuple(audit for audit in request.audit_entries if audit.id not in audit_ids)
        for sequence, audit in enumerate(new_audits, start=len(audit_ids) + 1):
            session.add(self._mapper.to_audit_model(audit, sequence))
