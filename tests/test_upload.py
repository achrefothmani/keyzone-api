import os
import pytest
from uuid import UUID
from app.core.config import settings

@pytest.mark.asyncio
async def test_upload_property_image(authed_client, db):
    # 1. Create a property first
    prop_payload = {
        "title": "Test Property for Upload",
        "type": "Villa",
        "vocation": "Vente",
        "city": "Tunis",
        "price": 500000.0
    }
    r = await authed_client.post("/api/v1/properties", json=prop_payload)
    assert r.status_code == 201
    prop_id = r.json()["id"]

    # 2. Upload an image
    file_content = b"fake image content"
    files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
    data = {"is_cover": "true"}
    
    r = await authed_client.post(
        f"/api/v1/properties/{prop_id}/images/upload",
        files=files,
        data=data
    )
    
    assert r.status_code == 201
    image_data = r.json()
    assert image_data["is_cover"] is True
    assert image_data["url"].startswith(f"{settings.BASE_URL}/uploads/properties/")
    assert image_data["url"].endswith(".jpg")

    # 3. Verify file exists on disk
    filename = image_data["url"].split("/")[-1]
    file_path = os.path.join(settings.UPLOAD_DIR, "properties", filename)
    assert os.path.exists(file_path)
    
    with open(file_path, "rb") as f:
        assert f.read() == file_content

    # Cleanup (optional but good practice)
    if os.path.exists(file_path):
        os.remove(file_path)
