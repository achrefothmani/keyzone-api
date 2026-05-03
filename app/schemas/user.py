from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    nom: str = Field(min_length=1, max_length=120)
    prenom: str = Field(min_length=1, max_length=120)
    telephone: str | None = None
    zone: str | None = Field(default=None, max_length=50)
    role: UserRole = UserRole.AGENT


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    nom: str | None = Field(default=None, max_length=120)
    prenom: str | None = Field(default=None, max_length=120)
    telephone: str | None = None
    zone: str | None = Field(default=None, max_length=50)
    role: UserRole | None = Field(default=None)
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserFilter(BaseModel):
    zone: str | None = None
    role: UserRole | None = None
    search: str | None = None
