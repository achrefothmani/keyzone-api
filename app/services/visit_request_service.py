from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.visit_request import VisitRequest
from app.models.notification import NotificationType
from app.repositories.visit_request_repository import VisitRequestRepository
from app.schemas.visit_request import VisitRequestCreate, VisitRequestUpdate
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService
from app.core.notifications import notification_manager

class VisitRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = VisitRequestRepository(db)
        self.notification_service = NotificationService(db)

    async def create(self, payload: VisitRequestCreate, source: str = "website") -> VisitRequest:
        request = VisitRequest(**payload.model_dump(), source=source)
        await self.repo.create(request)
        await self.db.commit()
        await self.db.refresh(request)

        # Broadcast that stats might have changed (new pending visit)
        await notification_manager.broadcast({"type": "STATS_UPDATE"})

        return request

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[VisitRequest], int]:
        return await self.repo.list(limit, offset)

    async def update(self, id: UUID, payload: VisitRequestUpdate) -> VisitRequest:
        request = await self.repo.get(id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit request not found")

        old_assigned_user_id = request.assigned_user_id
        old_status = request.status
        update_data = payload.model_dump(exclude_unset=True)
        new_assigned_user_id = update_data.get("assigned_user_id")
        new_status = update_data.get("status")

        await self.repo.update(request, update_data)

        # Notify if assignment changed
        if new_assigned_user_id and new_assigned_user_id != old_assigned_user_id:
            await self.notification_service.create_notification(
                NotificationCreate(
                    user_id=new_assigned_user_id,
                    title="Nouvelle visite assignée",
                    message=f"Une visite vous a été assignée pour la propriété {request.property_reference}",
                    type=NotificationType.VISIT_ASSIGNED,
                    link="/visites"
                    )
                    )

        # Broadcast if status changed (might affect sidebar dot)
        if new_status and new_status != old_status:
            await notification_manager.broadcast({"type": "STATS_UPDATE"})

        await self.db.commit()
        await self.db.refresh(request)
        return request


    async def delete(self, id: UUID) -> None:
        request = await self.repo.get(id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit request not found")
        
        await self.repo.delete(request)
        await self.db.commit()

        # Broadcast that stats might have changed
        await notification_manager.broadcast({"type": "STATS_UPDATE"})
