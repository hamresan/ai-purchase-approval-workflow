from decimal import Decimal
from uuid import UUID, uuid4

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.infrastructure.trusted_data.budget_reader import (
    SqlAlchemyBudgetConstraintReader,
)
from ai_purchase_workflow.infrastructure.trusted_data.catalog_reader import (
    SqlAlchemyTrustedCatalogReader,
)
from ai_purchase_workflow.infrastructure.trusted_data.models import (
    DepartmentMembershipModel,
    OrganizationMemberModel,
)
from ai_purchase_workflow.presentation.app import create_app

REQUESTER_ID = UUID("11111111-1111-1111-1111-111111111111")
UNKNOWN_ID = UUID("99999999-9999-9999-9999-999999999999")


async def _client(
    session_factory: async_sessionmaker[AsyncSession],
    database_url: str,
) -> AsyncClient:
    app = create_app(Settings(database_url=database_url, app_env="test"))
    app.state.session_factory = session_factory
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_non_admin_cannot_mutate_admin_resources(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    async with await _client(session_factory, test_database_url) as client:
        response = await client.post(
            "/api/admin/products",
            headers={"X-E2E-Actor": "requester"},
            json={"name": "Admin-only product"},
        )

    assert response.status_code == 403


async def test_admin_product_create_conflict_and_missing_update(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    async with await _client(session_factory, test_database_url) as client:
        created = await client.post(
            "/api/admin/products",
            headers={"X-E2E-Actor": "admin"},
            json={"name": "Dock"},
        )
        conflict = await client.post(
            "/api/admin/products",
            headers={"X-E2E-Actor": "admin"},
            json={"name": "Dock"},
        )
        missing = await client.put(
            f"/api/admin/products/{UNKNOWN_ID}",
            headers={"X-E2E-Actor": "admin"},
            json={"name": "Missing", "is_active": True},
        )

    assert created.status_code == 201
    assert conflict.status_code == 409
    assert missing.status_code == 404


async def test_admin_resource_validation_rejects_invalid_values(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    async with await _client(session_factory, test_database_url) as client:
        invalid_offer = await client.post(
            "/api/admin/offers",
            headers={"X-E2E-Actor": "admin"},
            json={
                "product_id": str(uuid4()),
                "vendor_id": str(uuid4()),
                "unit_price_amount": "0",
                "currency": "US",
                "available_quantity": -1,
            },
        )
        invalid_budget = await client.post(
            "/api/admin/budgets",
            headers={"X-E2E-Actor": "admin"},
            json={
                "owner_type": "USER",
                "user_id": None,
                "department_id": str(uuid4()),
                "amount": "500",
                "currency": "USD",
            },
        )

    assert invalid_offer.status_code == 422
    assert invalid_budget.status_code == 422


async def test_admin_catalog_mutations_are_consumed_by_trusted_reader(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    async with await _client(session_factory, test_database_url) as client:
        product = await client.post(
            "/api/admin/products",
            headers={"X-E2E-Actor": "admin"},
            json={"name": "USB-C hub"},
        )
        vendor = await client.post(
            "/api/admin/vendors",
            headers={"X-E2E-Actor": "admin"},
            json={"name": "Trusted Devices"},
        )
        offer = await client.post(
            "/api/admin/offers",
            headers={"X-E2E-Actor": "admin"},
            json={
                "product_id": product.json()["id"],
                "vendor_id": vendor.json()["id"],
                "unit_price_amount": "49.90",
                "currency": "usd",
                "available_quantity": 7,
            },
        )

    assert product.status_code == 201
    assert vendor.status_code == 201
    assert offer.status_code == 201

    async with session_factory() as session:
        item = await SqlAlchemyTrustedCatalogReader(session).find_item("USB-C hubs")

    assert item.description == "USB-C hub"
    assert item.vendor_name == "Trusted Devices"
    assert item.unit_price.amount == Decimal("49.90")
    assert item.unit_price.currency == "USD"
    assert item.available_quantity == 7


async def test_admin_department_budget_is_consumed_by_trusted_reader(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    async with await _client(session_factory, test_database_url) as client:
        department = await client.post(
            "/api/admin/departments",
            headers={"X-E2E-Actor": "admin"},
            json={"name": "Platform"},
        )
        budget = await client.post(
            "/api/admin/budgets",
            headers={"X-E2E-Actor": "admin"},
            json={
                "owner_type": "DEPARTMENT",
                "department_id": department.json()["id"],
                "user_id": None,
                "amount": "1200.00",
                "currency": "usd",
            },
        )

    assert department.status_code == 201
    assert budget.status_code == 201

    async with session_factory() as session:
        member = OrganizationMemberModel(
            id=uuid4(),
            identity_user_id=REQUESTER_ID,
            is_active=True,
        )
        session.add(member)
        await session.flush()
        session.add(
            DepartmentMembershipModel(
                member_id=member.id,
                department_id=UUID(department.json()["id"]),
                is_active=True,
            )
        )
        await session.commit()
        constraints = await SqlAlchemyBudgetConstraintReader(
            session
        ).get_applicable_constraints(REQUESTER_ID, "USD")

    assert [(item.owner_type, item.available.amount) for item in constraints] == [
        ("DEPARTMENT", Decimal("1200.00"))
    ]
