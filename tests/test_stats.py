import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Property, PropertyValidationStatus

@pytest.mark.asyncio
async def test_get_dashboard_stats_with_data(authed_client: AsyncClient, db: AsyncSession):
    # 1. Seed properties using the db fixture
    # One validated property
    prop1 = Property(
        reference="P-TEST-001",
        title="Property Validated",
        type="Appartement",
        vocation="Vente",
        city="Tunis",
        price=300000,
        validation=PropertyValidationStatus.VALIDATED
    )
    
    # One pending validation property
    prop2 = Property(
        reference="P-TEST-002",
        title="Property Pending",
        type="Villa",
        vocation="Vente",
        city="Marsa",
        price=1500000,
        validation=PropertyValidationStatus.PENDING
    )
    
    # One draft property (should not count in total if total means validated/pending? 
    # Wait, usually "total properties" means all non-deleted properties.
    # Let's check the implementation of the stats endpoint if possible.)
    
    db.add_all([prop1, prop2])
    await db.commit()

    # 2. Request stats
    response = await authed_client.get("/api/v1/stats/dashboard")
    assert response.status_code == 200
    data = response.json()

    # 3. Verify Full Schema
    # Ensure total_properties and pending_validation are present
    assert "total_properties" in data
    assert "pending_validation" in data
    assert "scheduled_visits" in data
    assert "property_views" in data
    
    # Check for trend fields (they can be null/default)
    for key in ["total_properties", "pending_validation", "scheduled_visits", "property_views"]:
        assert "value" in data[key]
        assert "trend_value" in data[key]
        assert "trend_positive" in data[key]

    # 4. Verify Counts
    # Assuming total_properties includes all seeded properties (2)
    # and pending_validation includes only prop2 (1)
    assert data["total_properties"]["value"] == 2
    assert data["pending_validation"]["value"] == 1
    # scheduled_visits and property_views should be 0 as we haven't seeded visit requests 
    # and no Umami DB is configured for tests
    assert data["scheduled_visits"]["value"] == 0
    assert data["property_views"]["value"] == 0
