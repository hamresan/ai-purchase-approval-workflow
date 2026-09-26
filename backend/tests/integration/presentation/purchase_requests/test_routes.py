from httpx import AsyncClient


async def test_create_retrieve_and_filter_purchase_requests(api_client: AsyncClient) -> None:
    create_response = await api_client.post(
        "/api/purchase-requests",
        json={
            "requester_name": "Dana",
            "items": [
                {
                    "description": "Laptop stand",
                    "quantity": 2,
                    "unit_price_amount": "35.00",
                    "currency": "usd",
                    "vendor": "Acme",
                }
            ],
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "drafting"
    assert created["items"][0]["currency"] == "USD"

    get_response = await api_client.get(f"/api/purchase-requests/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == created

    list_response = await api_client.get("/api/purchase-requests", params={"status": "drafting"})
    assert list_response.status_code == 200
    payload = list_response.json()
    assert [item["id"] for item in payload["items"]] == [created["id"]]
    assert payload["total"] == 1
    assert payload["limit"] == 20
    assert payload["offset"] == 0


async def test_get_unknown_purchase_request_returns_safe_404(api_client: AsyncClient) -> None:
    response = await api_client.get("/api/purchase-requests/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Purchase request not found."}


async def test_create_rejects_invalid_items(api_client: AsyncClient) -> None:
    response = await api_client.post(
        "/api/purchase-requests",
        json={
            "items": [
                {
                    "description": "",
                    "quantity": 1,
                    "unit_price_amount": "10.00",
                    "currency": "USD",
                }
            ]
        },
    )

    assert response.status_code == 422


async def test_prepare_uses_trusted_fixture_data(api_client: AsyncClient) -> None:
    created = (
        await api_client.post(
            "/api/purchase-requests",
            json={
                "requester_name": "Dana",
                "items": [
                    {
                        "description": "Laptop stand",
                        "quantity": 2,
                        "unit_price_amount": "999.00",
                        "currency": "USD",
                        "vendor": "Untrusted Vendor",
                    }
                ],
            },
        )
    ).json()

    response = await api_client.post(f"/api/purchase-requests/{created['id']}/prepare")

    assert response.status_code == 200
    assert response.json()["status"] == "pending_approval"


async def test_submit_before_approval_is_rejected_by_api(api_client: AsyncClient) -> None:
    created = (
        await api_client.post(
            "/api/purchase-requests",
            json={
                "requester_name": "Dana",
                "items": [
                    {
                        "description": "Laptop stand",
                        "quantity": 1,
                        "unit_price_amount": "35.00",
                        "currency": "USD",
                    }
                ],
            },
        )
    ).json()

    response = await api_client.post(f"/api/purchase-requests/{created['id']}/submit")

    assert response.status_code == 422
    assert response.json() == {
        "detail": "An approved decision is required before order submission."
    }


async def test_prepare_rejects_unknown_vendor_data(api_client: AsyncClient) -> None:
    created = (
        await api_client.post(
            "/api/purchase-requests",
            json={
                "requester_name": "Dana",
                "items": [
                    {
                        "description": "Unknown item",
                        "quantity": 1,
                        "unit_price_amount": "1.00",
                        "currency": "USD",
                    }
                ],
            },
        )
    ).json()

    response = await api_client.post(f"/api/purchase-requests/{created['id']}/prepare")

    assert response.status_code == 422
    assert "No trusted vendor data" in response.json()["detail"]


async def test_prepare_rejects_unavailable_quantity(api_client: AsyncClient) -> None:
    created = (
        await api_client.post(
            "/api/purchase-requests",
            json={
                "requester_name": "Dana",
                "items": [
                    {
                        "description": "Laptop stand",
                        "quantity": 11,
                        "unit_price_amount": "1.00",
                        "currency": "USD",
                    }
                ],
            },
        )
    ).json()

    response = await api_client.post(f"/api/purchase-requests/{created['id']}/prepare")

    assert response.status_code == 422
    assert "unavailable" in response.json()["detail"]


async def test_prepare_rejects_over_budget(api_client: AsyncClient) -> None:
    created = (
        await api_client.post(
            "/api/purchase-requests",
            json={
                "requester_name": "Dana",
                "items": [
                    {
                        "description": "Monitor",
                        "quantity": 3,
                        "unit_price_amount": "1.00",
                        "currency": "USD",
                    }
                ],
            },
        )
    ).json()

    response = await api_client.post(f"/api/purchase-requests/{created['id']}/prepare")

    assert response.status_code == 422
    assert "exceeds the available budget" in response.json()["detail"]


async def test_prepare_rejects_missing_budget_data(api_client: AsyncClient) -> None:
    created = (
        await api_client.post(
            "/api/purchase-requests",
            json={
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
    ).json()

    response = await api_client.post(f"/api/purchase-requests/{created['id']}/prepare")

    assert response.status_code == 422
    assert "No trusted budget data" in response.json()["detail"]


async def test_list_validates_pagination_and_order(api_client: AsyncClient) -> None:
    invalid_limit = await api_client.get("/api/purchase-requests", params={"limit": 0})
    invalid_offset = await api_client.get("/api/purchase-requests", params={"offset": -1})
    invalid_order = await api_client.get("/api/purchase-requests", params={"order": "newest"})

    assert invalid_limit.status_code == 422
    assert invalid_offset.status_code == 422
    assert invalid_order.status_code == 422


async def test_create_is_idempotent_for_same_key(api_client: AsyncClient) -> None:
    payload = {
        "requester_name": "Dana",
        "items": [
            {
                "description": "Laptop stand",
                "quantity": 1,
                "unit_price_amount": "35.00",
                "currency": "USD",
            }
        ],
    }
    headers = {"Idempotency-Key": "create-dana-stand"}

    first = await api_client.post("/api/purchase-requests", json=payload, headers=headers)
    second = await api_client.post("/api/purchase-requests", json=payload, headers=headers)
    listed = await api_client.get("/api/purchase-requests")

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["id"] == first.json()["id"]
    assert listed.json()["total"] == 1


async def test_list_supports_pagination(api_client: AsyncClient) -> None:
    for description in ("First", "Second", "Third"):
        response = await api_client.post(
            "/api/purchase-requests",
            json={
                "items": [
                    {
                        "description": description,
                        "quantity": 1,
                        "unit_price_amount": "1.00",
                        "currency": "USD",
                    }
                ]
            },
        )
        assert response.status_code == 201

    response = await api_client.get(
        "/api/purchase-requests",
        params={"limit": 2, "offset": 1, "order": "asc"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == 3
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    assert len(payload["items"]) == 2


async def test_response_contains_request_id_header(api_client: AsyncClient) -> None:
    response = await api_client.get(
        "/api/purchase-requests/00000000-0000-0000-0000-000000000000",
        headers={"X-Request-ID": "trace-123"},
    )

    assert response.headers["X-Request-ID"] == "trace-123"
