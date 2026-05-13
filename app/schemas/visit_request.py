from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.user import UserOut


class VisitRequestBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=8, max_length=40)
    email: EmailStr | None = None
    property_reference: str = Field(..., max_length=32)


class VisitRequestCreate(VisitRequestBase):
    pass


class VisitRequestUpdate(BaseModel):
    assigned_user_id: UUID | None = None
    visit_date: datetime | None = None
    status: str | None = None
    notes: str | None = None


class VisitRequestOut(VisitRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    assigned_user_id: UUID | None
    assigned_user: UserOut | None = None
    visit_date: datetime | None
    status: str
    source: str
    notes: str | None
