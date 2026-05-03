import pytest
from sqlalchemy import select
from app.models.property import Property
from app.repositories.property_repository import PropertyRepository

@pytest.mark.asyncio
async def test_get_max_reference_number(db):
    repo = PropertyRepository(db)
    
    # Test empty DB
    assert await repo.get_max_reference_number() is None
    
    # Test with some P references
    # Note: Use the new P prefix format
    p1 = Property(reference="P1000", title="T1", city="C", type="T", vocation="V", price=100)
    p2 = Property(reference="P1005", title="T2", city="C", type="T", vocation="V", price=200)
    p3 = Property(reference="OTHER-1", title="T3", city="C", type="T", vocation="V", price=300)
    p4 = Property(reference="P-RANDOM", title="T4", city="C", type="T", vocation="V", price=400) # Should be ignored by regex
    db.add_all([p1, p2, p3, p4])
    await db.flush()
    
    max_ref = await repo.get_max_reference_number()
    assert max_ref == 1005
