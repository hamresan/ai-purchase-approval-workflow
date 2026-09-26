import asyncio
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.application.purchase_requests.fakes.workflow import (
    FakePurchaseRequestWorkflowGateway,
)
from tests.integration.presentation.purchase_requests.support import (
    create_pending_request,
    load_audit_event_types,
)

from ai_purchase_workflow.application.purchase_requests.approval import ApprovePurchaseRequest
from ai_purchase_workflow.domain.purchase_requests import (
    Money,
    PurchaseItem,
    PurchaseRequest,
    RequestStatus,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests import (
    SqlAlchemyPurchaseRequestRepository,
)


async def test_approval_api_approves_pending_request_and_records_audit(
    approval_api_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    request_id = await create_pending_request(approval_api_client)
    response = await approval_api_client.post(
        f"/api/purchase-requests/{request_id}/approval",
        json={"action": "approve", "decided_by": "manager", "reason": "Within policy."},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert "approval_approved" in await load_audit_event_types(db_session, request_id)


async def test_approval_api_rejects_pending_request_and_records_audit(
    approval_api_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    request_id = await create_pending_request(approval_api_client)
    response = await approval_api_client.post(
        f"/api/purchase-requests/{request_id}/approval",
        json={"action": "reject", "decided_by": "manager", "reason": "Not required."},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert "approval_rejected" in await load_audit_event_types(db_session, request_id)


async def test_approval_api_edits_revalidates_and_keeps_request_pending(
    approval_api_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    request_id = await create_pending_request(approval_api_client)
    response = await approval_api_client.post(
        f"/api/purchase-requests/{request_id}/approval",
        json={
            "action": "edit",
            "decided_by": "manager",
            "items": [{"description": "Monitor", "quantity": 1}],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending_approval"
    assert body["items"][0]["description"] == "Monitor"
    assert body["items"][0]["vendor"] is not None
    assert "approval_edited" in await load_audit_event_types(db_session, request_id)


async def test_concurrent_approvals_resume_workflow_once(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    gateway = FakePurchaseRequestWorkflowGateway()
    async with session_factory() as setup_session:
        repository = SqlAlchemyPurchaseRequestRepository(setup_session)
        request = PurchaseRequest.create(
            (PurchaseItem("Laptop stand", 1, Money(Decimal("35.00"), "USD")),),
            "Dana",
        )
        request.transition_to(RequestStatus.PENDING_APPROVAL)
        await repository.add(request)
        request_id = request.id

    async def approve(decided_by: str) -> None:
        async with session_factory() as session:
            use_case = ApprovePurchaseRequest(
                SqlAlchemyPurchaseRequestRepository(session),
                gateway,
            )
            await use_case.execute(request_id, decided_by=decided_by)

    await asyncio.gather(approve("manager-a"), approve("manager-b"))
    assert gateway.approved_request_ids == [request_id]
