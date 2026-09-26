from httpx import AsyncClient


async def test_openapi_documents_hardened_purchase_request_contract(
    api_client: AsyncClient,
) -> None:
    response = await api_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    create = schema["paths"]["/api/purchase-requests"]["post"]
    create_headers = {parameter["name"] for parameter in create["parameters"]}
    assert "Idempotency-Key" in create_headers

    listing = schema["paths"]["/api/purchase-requests"]["get"]
    list_parameters = {parameter["name"] for parameter in listing["parameters"]}
    assert {"status", "limit", "offset", "order"} <= list_parameters

    response_schema = listing["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema["$ref"].endswith("/PurchaseRequestListResponse")
