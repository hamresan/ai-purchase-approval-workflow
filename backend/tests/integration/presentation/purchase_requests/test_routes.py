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
    assert [item["id"] for item in list_response.json()] == [created["id"]]


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
