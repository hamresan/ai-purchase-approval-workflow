from decimal import Decimal
from typing import cast

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
    PurchaseRequestModel,
)


class PurchaseItemRecordMapper:
    @staticmethod
    def to_record(item: PurchaseItem) -> dict[str, object]:
        return {
            "description": item.description,
            "quantity": item.quantity,
            "unit_price_amount": str(item.unit_price.amount),
            "currency": item.unit_price.currency,
            "vendor": item.vendor,
        }

    @staticmethod
    def to_domain(record: dict[str, object]) -> PurchaseItem:
        return PurchaseItem(
            description=cast(str, record["description"]),
            quantity=cast(int, record["quantity"]),
            unit_price=Money(
                Decimal(cast(str, record["unit_price_amount"])),
                cast(str, record["currency"]),
            ),
            vendor=cast(str | None, record.get("vendor")),
        )


class PurchaseRequestPersistenceMapper:
    def __init__(self, item_mapper: PurchaseItemRecordMapper | None = None) -> None:
        self._item_mapper = item_mapper or PurchaseItemRecordMapper()

    def to_model(self, request: PurchaseRequest) -> PurchaseRequestModel:
        return PurchaseRequestModel(
            id=request.id,
            requester_name=request.requester_name,
            status=request.status.value,
            items=[self._item_mapper.to_record(item) for item in request.items],
            created_at=request.created_at,
            updated_at=request.updated_at,
        )

    def update_model(self, model: PurchaseRequestModel, request: PurchaseRequest) -> None:
        model.requester_name = request.requester_name
        model.status = request.status.value
        model.items = [self._item_mapper.to_record(item) for item in request.items]
        model.updated_at = request.updated_at

    def to_domain(
        self,
        model: PurchaseRequestModel,
        draft: DraftOrderModel | None,
        decision: ApprovalDecisionModel | None,
        audits: tuple[AuditEntryModel, ...],
    ) -> PurchaseRequest:
        items = tuple(self._item_mapper.to_domain(record) for record in model.items)
        draft_order = None
        if draft is not None:
            draft_order = DraftOrder(
                id=draft.id,
                request_id=draft.request_id,
                items=tuple(self._item_mapper.to_domain(record) for record in draft.items),
                total=Money(draft.total_amount, draft.currency),
                created_at=draft.created_at,
            )
        approval_decision = None
        if decision is not None:
            approval_decision = ApprovalDecision(
                id=decision.id,
                request_id=decision.request_id,
                outcome=ApprovalOutcome(decision.outcome),
                decided_by=decision.decided_by,
                reason=decision.reason,
                decided_at=decision.decided_at,
            )
        audit_entries = tuple(
            AuditEntry(
                id=audit.id,
                request_id=audit.request_id,
                event_type=audit.event_type,
                message=audit.message,
                occurred_at=audit.occurred_at,
            )
            for audit in audits
        )
        return PurchaseRequest(
            id=model.id,
            requester_name=model.requester_name,
            items=items,
            status=RequestStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            draft_order=draft_order,
            approval_decision=approval_decision,
            audit_entries=audit_entries,
        )


class PurchaseRequestRelatedRecordMapper:
    def __init__(self, item_mapper: PurchaseItemRecordMapper | None = None) -> None:
        self._item_mapper = item_mapper or PurchaseItemRecordMapper()

    def to_draft_model(self, draft: DraftOrder) -> DraftOrderModel:
        return DraftOrderModel(
            id=draft.id,
            request_id=draft.request_id,
            items=[self._item_mapper.to_record(item) for item in draft.items],
            total_amount=draft.total.amount,
            currency=draft.total.currency,
            created_at=draft.created_at,
        )

    def update_draft_model(self, model: DraftOrderModel, draft: DraftOrder) -> None:
        model.items = [self._item_mapper.to_record(item) for item in draft.items]
        model.total_amount = draft.total.amount
        model.currency = draft.total.currency
        model.created_at = draft.created_at

    @staticmethod
    def to_decision_model(decision: ApprovalDecision) -> ApprovalDecisionModel:
        return ApprovalDecisionModel(
            id=decision.id,
            request_id=decision.request_id,
            outcome=decision.outcome.value,
            decided_by=decision.decided_by,
            reason=decision.reason,
            decided_at=decision.decided_at,
        )

    @staticmethod
    def to_audit_model(audit: AuditEntry, sequence: int) -> AuditEntryModel:
        return AuditEntryModel(
            id=audit.id,
            request_id=audit.request_id,
            sequence=sequence,
            event_type=audit.event_type,
            message=audit.message,
            occurred_at=audit.occurred_at,
        )
