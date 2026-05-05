import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.property import Property

@pytest.mark.asyncio
async def test_list_public_properties_unauthenticated(
    client: AsyncClient, db: AsyncSession
):
    # Create one validated and one draft property
    prop_val = Property(
        reference="PUB001",
        title="Public Property",
        type="Villa",
        vocation="Vente",
        price=500000,
        city="Tunis",
        validation="Validée",
    )
    prop_draft = Property(
        reference="PRIV001",
        title="Private Property",
        type="Appartement",
        vocation="Location",
        price=1200,
        city="Sousse",
        validation="Brouillon",
    )
    db.add_all([prop_val, prop_draft])
    await db.commit()

    response = await client.get("/api/v1/public/properties")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    
    # Check that only validated property is returned
    references = [p["reference"] for p in data["items"]]
    assert "PUB001" in references
    assert "PRIV001" not in references
    
    # Check that sensitive fields are missing
    for item in data["items"]:
        assert "owner_name" not in item
        assert "owner_phone" not in item
        assert "owner_email" not in item
        assert "responsible_id" not in item

@pytest.mark.asyncio
async def test_public_properties_filtering(
    client: AsyncClient, db: AsyncSession
):
    # Create two validated properties in different cities
    p1 = Property(
        reference="FILT001", title="P1", type="Villa", vocation="Vente",
        price=100, city="Tunis", validation="Validée"
    )
    p2 = Property(
        reference="FILT002", title="P2", type="Villa", vocation="Vente",
        price=200, city="Nabeul", validation="Validée"
    )
    db.add_all([p1, p2])
    await db.commit()

    # Filter by city
    response = await client.get("/api/v1/public/properties?city=Tunis")
    assert response.status_code == 200
    data = response.json()
    assert any(p["reference"] == "FILT001" for p in data["items"])
    assert not any(p["reference"] == "FILT002" for p in data["items"])

@pytest.mark.asyncio
async def test_public_properties_sub_type_filter(
    client: AsyncClient, db: AsyncSession
):
    # Create two validated properties with different sub_types
    p1 = Property(
        reference="ST001", title="S1", type="Villa", vocation="Vente",
        price=100, city="Tunis", validation="Validée", sub_type="Villa individuelle"
    )
    p2 = Property(
        reference="ST002", title="S2", type="Villa", vocation="Vente",
        price=200, city="Tunis", validation="Validée", sub_type="Villa jumelée"
    )
    db.add_all([p1, p2])
    await db.commit()

    # Filter by sub_type
    response = await client.get("/api/v1/public/properties?sub_type=Villa+individuelle")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["reference"] == "ST001"
    assert data["items"][0]["sub_type"] == "Villa individuelle"
