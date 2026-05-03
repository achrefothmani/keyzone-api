from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.api.deps import CurrentUser, DBSession, get_property_filters
from app.schemas.common import Page
from app.schemas.property import (
    PropertyCreate,
    PropertyFilter,
    PropertyHistoryOut,
    PropertyImageCreate,
    PropertyImageOut,
    PropertyOut,
    PropertyUpdate,
)
from app.services.property_service import PropertyService

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("", response_model=Page[PropertyOut])
async def list_properties(
    db: DBSession,
    _: CurrentUser,
    filters: PropertyFilter = Depends(get_property_filters),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> Page[PropertyOut]:
    items, total = await PropertyService(db).list(filters, limit, offset)
    return Page[PropertyOut](
        items=[PropertyOut.model_validate(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
async def create_property(
    payload: PropertyCreate, db: DBSession, current_user: CurrentUser
) -> PropertyOut:
    prop = await PropertyService(db).create(payload, current_user)
    return PropertyOut.model_validate(prop)


@router.get("/{property_id}", response_model=PropertyOut)
async def get_property(
    property_id: UUID, db: DBSession, _: CurrentUser
) -> PropertyOut:
    prop = await PropertyService(db).get(property_id)
    return PropertyOut.model_validate(prop)


@router.get("/{property_id}/history", response_model=list[PropertyHistoryOut])
async def get_property_history(
    property_id: UUID, db: DBSession, _: CurrentUser
) -> list[PropertyHistoryOut]:
    items = await PropertyService(db).list_history(property_id)
    return [PropertyHistoryOut.model_validate(i) for i in items]


@router.put("/{property_id}", response_model=PropertyOut)
async def update_property(
    property_id: UUID,
    payload: PropertyUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> PropertyOut:
    prop = await PropertyService(db).update(property_id, payload, current_user)
    return PropertyOut.model_validate(prop)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: UUID, db: DBSession, current_user: CurrentUser
) -> None:
    await PropertyService(db).delete(property_id, current_user)


@router.get("/{property_id}/images", response_model=list[PropertyImageOut])
async def list_images(
    property_id: UUID, db: DBSession, _: CurrentUser
) -> list[PropertyImageOut]:
    items = await PropertyService(db).list_images(property_id)
    return [PropertyImageOut.model_validate(i) for i in items]


@router.post(
    "/{property_id}/images",
    response_model=PropertyImageOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_image(
    property_id: UUID,
    payload: PropertyImageCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> PropertyImageOut:
    image = await PropertyService(db).add_image(property_id, payload, current_user)
    return PropertyImageOut.model_validate(image)


@router.post(
    "/{property_id}/images/upload",
    response_model=PropertyImageOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    property_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    is_cover: bool = Form(False),
) -> PropertyImageOut:
    image = await PropertyService(db).upload_image(property_id, file, current_user, is_cover)
    return PropertyImageOut.model_validate(image)


@router.delete(
    "/{property_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_image(
    property_id: UUID,
    image_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    await PropertyService(db).delete_image(image_id, current_user)


@router.patch(
    "/{property_id}/images/{image_id}/set-cover",
    response_model=PropertyImageOut,
)
async def set_image_as_cover(
    property_id: UUID,
    image_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> PropertyImageOut:
    image = await PropertyService(db).set_image_as_cover(
        property_id, image_id, current_user
    )
    return PropertyImageOut.model_validate(image)
