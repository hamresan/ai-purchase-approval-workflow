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

    async def sync_to_session(
        self,
        session: AsyncSession,
        request: PurchaseRequest,
    ) -> None:
        await self._sync_draft(session, request)
        await self._add_missing_decision(session, request)
        await self._add_missing_audits(session, request)

    async def _sync_draft(self, session: AsyncSession, request: PurchaseRequest) -> None:
        if request.draft_order is None:
            return
        model = await session.scalar(
            select(DraftOrderModel).where(DraftOrderModel.request_id == request.id)
        )
        if model is None:
            session.add(self._mapper.to_draft_model(request.draft_order))
            return
        self._mapper.update_draft_model(model, request.draft_order)

    async def _add_missing_decision(
        self,
        session: AsyncSession,
        request: PurchaseRequest,
    ) -> None:
        if request.approval_decision is None:
            return
        exists = await session.scalar(
            select(ApprovalDecisionModel.id).where(
                ApprovalDecisionModel.id == request.approval_decision.id
            )
        )
        if exists is None:
            session.add(self._mapper.to_decision_model(request.approval_decision))

    async def _add_missing_audits(
        self,
        session: AsyncSession,
        request: PurchaseRequest,
    ) -> None:
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
