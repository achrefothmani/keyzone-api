import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_visit_request(client: AsyncClient):
    payload = {
        "full_name": "John Doe",
        "phone": "555-0123-456",
        "email": "john@example.com",
        "property_reference": "REF123"
    }
    response = await client.post("/api/v1/public/visit-requests", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert data["property_reference"] == "REF123"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_visit_request_invalid_phone(client: AsyncClient):
    payload = {
        "full_name": "John Doe",
        "phone": "123", # too short
        "property_reference": "REF123"
    }
    response = await client.post("/api/v1/public/visit-requests", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_visit_request(authed_client: AsyncClient, client: AsyncClient):
    # 1. Create a request
    payload = {
        "full_name": "To Delete",
        "phone": "555-0123-456",
        "property_reference": "REF_DEL"
    }
    create_res = await client.post("/api/v1/public/visit-requests", json=payload)
    visit_id = create_res.json()["id"]

    # 2. Delete it
    delete_res = await authed_client.delete(f"/api/v1/visit-requests/{visit_id}")
    assert delete_res.status_code == 204

    # 3. Verify it's gone
    get_res = await authed_client.get("/api/v1/visit-requests")
    items = get_res.json()["items"]
    assert not any(i["id"] == visit_id for i in items)


@pytest.mark.asyncio
async def test_update_visit_request_with_timezone(authed_client: AsyncClient, client: AsyncClient):
    # 1. Create a request
    payload = {
        "full_name": "TZ Test",
        "phone": "555-0123-456",
        "property_reference": "REF_TZ"
    }
    create_res = await client.post("/api/v1/public/visit-requests", json=payload)
    visit_id = create_res.json()["id"]

    # 2. Update it with a timezone-aware datetime (UTC)
    from datetime import datetime, timezone
    visit_date = datetime.now(timezone.utc).isoformat()
    
    update_res = await authed_client.patch(
        f"/api/v1/visit-requests/{visit_id}",
        json={"visit_date": visit_date, "status": "confirmed"}
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["status"] == "confirmed"
    assert data["visit_date"] is not None
