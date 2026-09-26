from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.infrastructure.persistence.models import AuditEntryModel


async def create_pending_request(client: AsyncClient) -> UUID:
    created_response = await client.post(
        "/api/purchase-requests",
        json={
            "requester_name": "Dana",
            "items": [
                {
                    "description": "Laptop stand",
                    "quantity": 1,
                    "unit_price_amount": "1.00",
                    "currency": "USD",
                }
            ],
        },
    )
    assert created_response.status_code == 201
    request_id = UUID(created_response.json()["id"])
    prepared_response = await client.post(f"/api/purchase-requests/{request_id}/prepare")
    assert prepared_response.status_code == 200
    return request_id


async def load_audit_event_types(session: AsyncSession, request_id: UUID) -> list[str]:
    statement = (
        select(AuditEntryModel.event_type)
        .where(AuditEntryModel.request_id == request_id)
        .order_by(AuditEntryModel.sequence)
    )
    return list((await session.scalars(statement)).all())
