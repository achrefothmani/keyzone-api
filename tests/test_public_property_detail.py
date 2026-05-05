import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_public_property_by_reference(client: AsyncClient, db):
    # Setup: Create a validated property
    from app.models.property import Property
    from app.models.user import User, UserRole
    import uuid

    # Create a user for responsible_id
    user = User(
        nom="Test",
        prenom="User",
        email=f"test_{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="...",
        role=UserRole.AGENT,
    )
    db.add(user)
    await db.flush()
    
    prop = Property(
        id=uuid.uuid4(),
        reference="REF123",
        title="Public Property",
        type="Villa",
        vocation="Vente",
        price=500000,
        city="Tunis",
        validation="Validée",
        responsible_id=user.id
    )
    db.add(prop)
    await db.commit()

    response = await client.get(f"/api/v1/public/properties/REF123")
    assert response.status_code == 200
    data = response.json()
    assert data["reference"] == "REF123"
    assert data["title"] == "Public Property"

@pytest.mark.asyncio
async def test_get_public_property_by_reference_not_validated(client: AsyncClient, db):
    # Setup: Create a non-validated property
    from app.models.property import Property
    from app.models.user import User, UserRole
    import uuid

    user = User(
        nom="Test",
        prenom="User",
        email=f"test_{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="...",
        role=UserRole.AGENT,
    )
    db.add(user)
    await db.flush()

    prop = Property(
        id=uuid.uuid4(),
        reference="REF456",
        title="Draft Property",
        type="Villa",
        vocation="Vente",
        price=500000,
        city="Tunis",
        validation="Brouillon",
        responsible_id=user.id
    )
    db.add(prop)
    await db.commit()

    response = await client.get(f"/api/v1/public/properties/REF456")
    assert response.status_code == 404
