from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PropertyImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    is_cover: bool
    created_at: datetime


class PropertyImageCreate(BaseModel):
    url: str = Field(min_length=1, max_length=1024)
    is_cover: bool = False


class PropertyBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=50)
    sub_type: str | None = Field(default=None, max_length=50)
    status: str = Field(default="Disponible", min_length=1, max_length=50)
    vocation: str = Field(min_length=1, max_length=50)
    validation: str = Field(default="Brouillon", min_length=1, max_length=50)
    price: float = Field(ge=0)
    currency: str = Field(default="TND", min_length=3, max_length=3)
    surface: float | None = Field(default=None, ge=0)
    rooms: int | None = Field(default=None, ge=0)
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: int | None = Field(default=None, ge=0)
    floor: int | None = None
    furnished: bool = False
    description: str | None = None
    address: str | None = None
    city: str = Field(min_length=1, max_length=120)
    neighborhood: str | None = None
    postal_code: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    owner_name: str | None = None
    owner_phone: str | None = None
    owner_email: EmailStr | None = None
    responsible_id: UUID | None = None


class PropertyCreate(PropertyBase):
    reference: str | None = Field(default=None, max_length=32)
    images: list[PropertyImageCreate] = Field(default_factory=list)


class PropertyUpdate(BaseModel):
    title: str | None = None
    type: str | None = None
    sub_type: str | None = Field(default=None, max_length=50)
    status: str | None = None
    vocation: str | None = None
    validation: str | None = None
    price: float | None = Field(default=None, ge=0)
    currency: str | None = None
    surface: float | None = None
    rooms: int | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    floor: int | None = None
    furnished: bool | None = None
    description: str | None = None
    address: str | None = None
    city: str | None = None
    neighborhood: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    owner_name: str | None = None
    owner_phone: str | None = None
    owner_email: EmailStr | None = None
    responsible_id: UUID | None = None


class PropertyResponsible(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nom: str
    prenom: str
    email: EmailStr


class PropertyHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: UUID
    user: PropertyResponsible | None = None
    action: str
    changes: dict | None = None
    created_at: datetime


class PropertyOut(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reference: str
    created_at: datetime
    updated_at: datetime
    responsible: PropertyResponsible | None = None
    images: list[PropertyImageOut] = Field(default_factory=list)


class PropertyFilter(BaseModel):
    reference: str | None = None
    title: str | None = None
    type: str | None = None
    sub_type: str | None = Field(default=None, max_length=50)
    vocation: str | None = None
    status: str | None = None
    validation: str | None = None
    currency: str | None = None
    city: str | None = None
    neighborhood: str | None = None
    postal_code: str | None = None
    furnished: bool | None = None
    rooms: int | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    floor: int | None = None

    # Ranges
    min_price: float | None = None
    max_price: float | None = None
    min_surface: float | None = None
    max_surface: float | None = None
    min_rooms: int | None = None
    max_rooms: int | None = None
    min_bedrooms: int | None = None
    max_bedrooms: int | None = None
    min_bathrooms: int | None = None
    max_bathrooms: int | None = None
    min_floor: int | None = None
    max_floor: int | None = None

    # Other
    responsible_id: UUID | None = None
    owner_name: str | None = None
    owner_phone: str | None = None
    owner_email: str | None = None
    search: str | None = None
    sort_by: str = Field(default="created_at", pattern="^(price|created_at|updated_at)$")
    sort_dir: str = Field(default="desc", pattern="^(asc|desc)$")
