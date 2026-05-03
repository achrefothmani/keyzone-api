import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_sequential_reference_generation(authed_client: AsyncClient):
    # Create first property
    data = {
        "title": "Prop 1", "type": "Appartement", "vocation": "Vente",
        "price": 100000, "city": "Tunis", "images": []
    }
    r1 = await authed_client.post("/api/v1/properties", json=data)
    assert r1.status_code == 201
    assert r1.json()["reference"] == "P1000"

    # Create second property
    r2 = await authed_client.post("/api/v1/properties", json=data)
    assert r2.status_code == 201
    assert r2.json()["reference"] == "P1001"
