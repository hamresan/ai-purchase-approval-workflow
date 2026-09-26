import asyncio

from httpx import AsyncClient


async def test_concurrent_create_with_same_idempotency_key_returns_one_request(
    api_client: AsyncClient,
) -> None:
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
    headers = {"Idempotency-Key": "concurrent-create"}

    first, second = await asyncio.gather(
        api_client.post("/api/purchase-requests", json=payload, headers=headers),
        api_client.post("/api/purchase-requests", json=payload, headers=headers),
    )
    listed = await api_client.get("/api/purchase-requests")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert listed.json()["total"] == 1
