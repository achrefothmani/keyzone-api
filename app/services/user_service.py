from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserFilter, UserUpdate
from app.utils.text import email_local_part


def _build_email(prenom: str, nom: str, suffix: int = 0) -> str:
    base = email_local_part(prenom, nom)
    if suffix:
        base = f"{base}{suffix}"
    return f"{base}@{settings.EMAIL_DOMAIN}"


async def _resolve_unique_email(repo: UserRepository, prenom: str, nom: str) -> str:
    suffix = 0
    while True:
        candidate = _build_email(prenom, nom, suffix)
        if not await repo.email_exists(candidate):
            return candidate
        suffix += 1


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def create(self, payload: UserCreate) -> User:
        email = await _resolve_unique_email(self.repo, payload.prenom, payload.nom)
        user = User(
            nom=payload.nom,
            prenom=payload.prenom,
            telephone=payload.telephone,
            zone=payload.zone,
            role=payload.role,
            email=email,
            hashed_password=hash_password(payload.password),
        )
        await self.repo.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get(self, user_id: UUID | str) -> User:
        user = await self.repo.get(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return user

    async def list(
        self,
        filters: UserFilter,
        limit: int,
        offset: int,
    ) -> tuple[list[User], int]:
        return await self.repo.list(
            zone=filters.zone,
            role=filters.role,
            search=filters.search,
            limit=limit,
            offset=offset,
        )

    async def update(self, user_id: UUID | str, payload: UserUpdate) -> User:
        user = await self.get(user_id)
        prenom_changed = payload.prenom is not None and payload.prenom != user.prenom
        nom_changed = payload.nom is not None and payload.nom != user.nom

        if payload.nom is not None:
            user.nom = payload.nom
        if payload.prenom is not None:
            user.prenom = payload.prenom
        if payload.telephone is not None:
            user.telephone = payload.telephone
        if payload.zone is not None:
            user.zone = payload.zone
        if payload.role is not None:
            user.role = payload.role
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.password:
            user.hashed_password = hash_password(payload.password)

        if prenom_changed or nom_changed:
            user.email = await _resolve_unique_email(self.repo, user.prenom, user.nom)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: UUID | str) -> None:
        user = await self.get(user_id)
        await self.repo.delete(user)
        await self.db.commit()
