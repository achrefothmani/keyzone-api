import pytest

@pytest.mark.asyncio
async def test_list_public_properties(client):
    # This should be accessible without authentication
    r = await client.get("/api/v1/public/properties")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
