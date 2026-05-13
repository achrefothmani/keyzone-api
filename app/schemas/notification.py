from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationType


class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: NotificationType
    link: str | None = Field(default=None, max_length=512)
    is_read: bool = False


class NotificationCreate(NotificationBase):
    user_id: UUID


class NotificationUpdate(BaseModel):
    is_read: bool | None = None


class Notification(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
