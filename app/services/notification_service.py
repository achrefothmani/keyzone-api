from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.notifications import notification_manager
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import Notification as NotificationSchema
from app.schemas.notification import NotificationCreate


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationRepository(db)

    async def list_for_user(self, user_id: UUID, limit: int = 20) -> list[Notification]:
        return await self.repo.list_for_user(user_id, limit)

    async def mark_all_as_read(self, user_id: UUID) -> None:
        await self.repo.mark_all_as_read(user_id)
        await self.db.commit()

    async def create_notification(self, obj_in: NotificationCreate) -> Notification:
        notification = await self.repo.create(obj_in)
        await self.db.commit()
        await self.db.refresh(notification)

        # Push update via WebSocket
        ws_message = NotificationSchema.model_validate(notification).model_dump(mode="json")
        await notification_manager.send_personal_message(ws_message, obj_in.user_id)

        return notification
