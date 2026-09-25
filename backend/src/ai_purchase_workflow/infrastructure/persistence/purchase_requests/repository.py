from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus
from ai_purchase_workflow.infrastructure.persistence.models import (
    ApprovalDecisionModel,
    AuditEntryModel,
    DraftOrderModel,
    PurchaseRequestModel,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.mapper import (
    PurchaseItemRecordMapper,
    PurchaseRequestPersistenceMapper,
)


class SqlAlchemyPurchaseRequestRepository(PurchaseRequestRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: PurchaseRequestPersistenceMapper | None = None,
        item_mapper: PurchaseItemRecordMapper | None = None,
    ) -> None:
        self._session = session
        self._item_mapper = item_mapper or PurchaseItemRecordMapper()
        self._mapper = mapper or PurchaseRequestPersistenceMapper(self._item_mapper)

    async def add(self, request: PurchaseRequest) -> None:
        self._session.add(self._mapper.to_model(request))
        await self._write_related(request)
        await self._session.commit()

    async def get(self, request_id: UUID) -> PurchaseRequest | None:
        model = await self._session.get(PurchaseRequestModel, request_id)
        if model is None:
            return None
        return await self._load_domain(model)

    async def list(self, status: RequestStatus | None = None) -> tuple[PurchaseRequest, ...]:
        statement = select(PurchaseRequestModel)
        if status is not None:
            statement = statement.where(PurchaseRequestModel.status == status.value)
        statement = statement.order_by(PurchaseRequestModel.created_at, PurchaseRequestModel.id)
        models = (await self._session.scalars(statement)).all()
        return tuple([await self._load_domain(model) for model in models])

    async def _write_related(self, request: PurchaseRequest) -> None:
        if request.draft_order is not None:
            draft = request.draft_order
            self._session.add(
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
            self._session.add(
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
            self._session.add(
                AuditEntryModel(
                    id=audit.id,
                    request_id=audit.request_id,
                    sequence=sequence,
                    event_type=audit.event_type,
                    message=audit.message,
                    occurred_at=audit.occurred_at,
                )
            )

    async def _load_domain(self, model: PurchaseRequestModel) -> PurchaseRequest:
        draft = await self._session.scalar(
            select(DraftOrderModel).where(DraftOrderModel.request_id == model.id)
        )
        decision = await self._session.scalar(
            select(ApprovalDecisionModel).where(ApprovalDecisionModel.request_id == model.id)
        )
        audits = tuple(
            (await self._session.scalars(
                select(AuditEntryModel)
                .where(AuditEntryModel.request_id == model.id)
                .order_by(AuditEntryModel.sequence)
            )).all()
        )
        return self._mapper.to_domain(model, draft, decision, audits)
