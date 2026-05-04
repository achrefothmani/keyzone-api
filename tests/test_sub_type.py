import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_sub_type_field(authed_client: AsyncClient):
    # 1. Create with sub_type
    payload = {
        "title": "Test Sub Type",
        "type": "Villa",
        "sub_type": "Villa jumelée",
        "vocation": "Vente",
        "price": 1000000,
        "city": "Tunis",
    }
    r = await authed_client.post("/api/v1/properties", json=payload)
    assert r.status_code == 201, f"Failed to create: {r.text}"
    prop = r.json()
    assert prop["sub_type"] == "Villa jumelée"

    # 2. Filter by sub_type
    r = await authed_client.get("/api/v1/properties", params={"sub_type": "Villa jumelée"})
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 1
    assert items[0]["sub_type"] == "Villa jumelée"
