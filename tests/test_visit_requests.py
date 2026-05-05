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
