from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.services.property_service import PropertyService

router = APIRouter(prefix="/images", tags=["images"])


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: UUID, db: DBSession, current_user: CurrentUser
) -> None:
    await PropertyService(db).delete_image(image_id, current_user)
