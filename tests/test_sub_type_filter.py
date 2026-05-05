import pytest
from httpx import AsyncClient

async def _make_property(client, **overrides):
    payload = {
        "title": "Property Title",
        "type": "Villa",
        "vocation": "Vente",
        "status": "Disponible",
        "price": 1000000,
        "city": "Tunis",
        "sub_type": "Villa individuelle",
    }
    payload.update(overrides)
    r = await client.post("/api/v1/properties", json=payload)
    assert r.status_code == 201, r.text
    return r.json()

@pytest.mark.asyncio
async def test_filter_by_sub_type(authed_client: AsyncClient):
    await _make_property(authed_client, sub_type="Villa individuelle")
    await _make_property(authed_client, sub_type="Villa jumelée")
    
    # Filter by sub_type
    r = await authed_client.get("/api/v1/properties", params={"sub_type": "Villa individuelle"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["sub_type"] == "Villa individuelle"

    # Filter by another sub_type
    r = await authed_client.get("/api/v1/properties", params={"sub_type": "Villa jumelée"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["sub_type"] == "Villa jumelée"
