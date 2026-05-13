from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.user import User


class VisitRequest(UUIDPKMixin, TimestampMixin, Base):
    """
    Represents a request for a property visit.
    """
    __tablename__ = "requests"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    property_reference: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    assigned_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    visit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", server_default="pending", nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="website", server_default="website", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assigned_user: Mapped[User | None] = relationship("User")
