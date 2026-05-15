from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: UUID | str) -> User | None:
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return None
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email.lower())
        return (await self.db.execute(stmt)).first() is not None

    async def list(
        self,
        *,
        zone: str | None = None,
        role: UserRole | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        stmt = select(User)
        count_stmt = select(func.count(User.id))

        if zone is not None:
            stmt = stmt.where(User.zone == zone)
            count_stmt = count_stmt.where(User.zone == zone)
        if role is not None:
            stmt = stmt.where(User.role == role)
            count_stmt = count_stmt.where(User.role == role)
        if search:
            pattern = f"%{search.lower()}%"
            cond = or_(
                func.lower(User.nom).like(pattern),
                func.lower(User.prenom).like(pattern),
                func.lower(User.email).like(pattern),
            )
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)
        items = (await self.db.execute(stmt)).scalars().all()
        total = (await self.db.execute(count_stmt)).scalar_one()
        return list(items), int(total)

    async def get_users_by_roles(self, roles: list[UserRole]) -> list[User]:
        stmt = select(User).where(User.role.in_(roles), User.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def add(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
