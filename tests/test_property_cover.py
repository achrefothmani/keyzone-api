import pytest
from httpx import AsyncClient

async def _make_property(client, **overrides):
    payload = {
        "title": "Villa S+4 avec piscine",
        "type": "Villa",
        "vocation": "Vente",
        "status": "Disponible",
        "price": 1850000,
        "city": "La Marsa",
        "neighborhood": "Marsa Plage",
        "rooms": 6,
        "bedrooms": 4,
        "bathrooms": 3,
        "surface": 320,
        "furnished": False,
    }
    payload.update(overrides)
    r = await client.post("/api/v1/properties", json=payload)
    assert r.status_code == 201, r.text
    return r.json()

@pytest.mark.asyncio
async def test_set_image_as_cover(authed_client: AsyncClient):
    # 1. Create a property
    prop = await _make_property(authed_client)
    prop_id = prop["id"]
    
    # 2. Add two images
    img1_resp = await authed_client.post(
        f"/api/v1/properties/{prop_id}/images",
        json={"url": "http://example.com/1.jpg", "is_cover": True}
    )
    img2_resp = await authed_client.post(
        f"/api/v1/properties/{prop_id}/images",
        json={"url": "http://example.com/2.jpg", "is_cover": False}
    )
    
    assert img1_resp.status_code == 201
    assert img2_resp.status_code == 201
    
    img1_id = img1_resp.json()["id"]
    img2_id = img2_resp.json()["id"]
    
    # 3. Set second image as cover
    response = await authed_client.patch(
        f"/api/v1/properties/{prop_id}/images/{img2_id}/set-cover",
    )
    assert response.status_code == 200
    assert response.json()["is_cover"] is True
    
    # 4. Verify first image is no longer cover
    images_resp = await authed_client.get(
        f"/api/v1/properties/{prop_id}/images",
    )
    assert images_resp.status_code == 200
    images = images_resp.json()
    
    found_img1 = False
    found_img2 = False
    for img in images:
        if img["id"] == img1_id:
            assert img["is_cover"] is False
            found_img1 = True
        if img["id"] == img2_id:
            assert img["is_cover"] is True
            found_img2 = True
            
    assert found_img1
    assert found_img2
