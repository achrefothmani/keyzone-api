from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.user import User


class PropertyValidationStatus(str, enum.Enum):
    BROUILLON = "Brouillon"
    PENDING = "En attente de validation"
    VALIDATED = "Validée"


class PropertyType(str, enum.Enum):
    APPARTEMENT = "Appartement"
    VILLA = "Villa"
    TERRAIN = "Terrain"
    LOCAL = "Local"


class PropertySubType(str, enum.Enum):
    # Appartement
    STUDIO = "Studio"
    S_PLUS_1 = "S+1"
    S_PLUS_2 = "S+2"
    S_PLUS_3 = "S+3"
    S_PLUS_4 = "S+4"
    S_PLUS_5 = "S+5"
    DUPLEX = "Duplex"
    PENTHOUSE = "Penthouse"
    # Villa
    VILLA_JUMELEE = "Villa jumelée"
    VILLA_INDIVIDUELLE = "Villa individuelle"
    # Terrain
    TERRAIN_HABITATION = "Terrain habitation"
    TERRAIN_AGRICULTURE = "Terrain agriculture"
    TERRAIN_PROMOTION = "Terrain promotion"
    # Local
    LOCAL_COMMERCIAL = "Local commercial"
    LOCAL_BUREAUTIQUE = "Local bureautique"


class Property(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "properties"

    reference: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Keep as string for now to support migration
    sub_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Disponible",
    )
    vocation: Mapped[str] = mapped_column(String(50), nullable=False)
    validation: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Brouillon",
    )

    price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="TND", nullable=False)
    surface: Mapped[float | None] = mapped_column(Float, nullable=True)
    rooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bedrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    floor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    furnished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    neighborhood: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    owner_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    owner_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    responsible_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    responsible: Mapped["User | None"] = relationship(
        back_populates="properties", lazy="joined"
    )
    images: Mapped[List["PropertyImage"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    history: Mapped[List["PropertyHistory"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_properties_city", "city"),
        Index("ix_properties_price", "price"),
        Index("ix_properties_type", "type"),
        Index("ix_properties_vocation", "vocation"),
        Index("ix_properties_status", "status"),
        Index("ix_properties_responsible", "responsible_id"),
    )


class PropertyImage(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "property_images"

    property_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    property: Mapped["Property"] = relationship(back_populates="images")


class PropertyHistory(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "property_history"

    property_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    changes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    property: Mapped["Property"] = relationship(back_populates="history")
    user: Mapped["User | None"] = relationship(lazy="joined")
