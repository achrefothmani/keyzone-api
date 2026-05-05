from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class VisitRequestBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=8, max_length=40)
    email: EmailStr | None = None
    property_reference: str = Field(..., max_length=32)

class VisitRequestCreate(VisitRequestBase):
    pass

class VisitRequestOut(VisitRequestBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
