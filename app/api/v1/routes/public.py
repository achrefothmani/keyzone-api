from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.api.deps import DBSession, get_property_filters
from app.models.property import Property
from app.schemas.common import Page
from app.schemas.property import (
    PropertyFilter,
    PublicPropertyOut,
)
from app.services.property_service import PropertyService

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/properties", response_model=Page[PublicPropertyOut])
async def list_public_properties(
    db: DBSession,
    filters: PropertyFilter = Depends(get_property_filters),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> Page[PublicPropertyOut]:
    # Force validation status to only show validated properties
    filters.validation = "Validée"
    
    items, total = await PropertyService(db).list(filters, limit, offset)
    return Page[PublicPropertyOut](
        items=[PublicPropertyOut.model_validate(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/stats")
async def get_public_stats(db: DBSession):
    stmt = (
        select(func.count(Property.id))
        .where(Property.is_deleted.is_(False), Property.validation == "Validée")
    )
    total = (await db.execute(stmt)).scalar_one()
    return {"total_validated": total}
