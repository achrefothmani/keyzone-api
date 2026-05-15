from __future__ import annotations

import enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.property import Property


class UserRole(str, enum.Enum):
    AGENT = "AGENT"
    CHEF_AGENCE = "CHEF_AGENCE"
    COORDINATEUR = "COORDINATEUR"


class User(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "users"

    nom: Mapped[str] = mapped_column(String(120), nullable=False)
    prenom: Mapped[str] = mapped_column(String(120), nullable=False)
    telephone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, name="user_role_enum"),
        nullable=False,
        default=UserRole.AGENT,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    properties: Mapped[List["Property"]] = relationship(
        back_populates="responsible",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_zone", "zone"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.prenom} {self.nom}".strip()
