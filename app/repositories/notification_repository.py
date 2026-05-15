from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, obj_in: NotificationCreate) -> Notification:
        db_obj = Notification(
            user_id=obj_in.user_id,
            title=obj_in.title,
            message=obj_in.message,
            type=obj_in.type,
            link=obj_in.link,
            is_read=obj_in.is_read,
        )
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def list_for_user(
        self, user_id: UUID, limit: int = 20
    ) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_all_as_read(self, user_id: UUID) -> None:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
        )
        await self.db.execute(stmt)
        await self.db.flush()
