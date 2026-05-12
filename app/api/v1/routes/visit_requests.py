from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.common import Page
from app.schemas.visit_request import VisitRequestOut, VisitRequestUpdate
from app.services.visit_request_service import VisitRequestService

router = APIRouter(prefix="/visit-requests", tags=["visit-requests"])


@router.get("", response_model=Page[VisitRequestOut])
async def list_visit_requests(
    db: DBSession,
    _: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[VisitRequestOut]:
    items, total = await VisitRequestService(db).list(limit, offset)
    return Page[VisitRequestOut](
        items=[VisitRequestOut.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{id}", response_model=VisitRequestOut)
async def update_visit_request(
    id: UUID, payload: VisitRequestUpdate, db: DBSession, _: CurrentUser
) -> VisitRequestOut:
    item = await VisitRequestService(db).update(id, payload)
    return VisitRequestOut.model_validate(item)
