from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.visit_request import VisitRequest

class VisitRequestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, request: VisitRequest) -> VisitRequest:
        self.db.add(request)
        await self.db.flush()
        return request

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[VisitRequest], int]:
        from sqlalchemy import select, func
        from sqlalchemy.orm import joinedload
        stmt = (
            select(VisitRequest)
            .options(joinedload(VisitRequest.assigned_user))
            .order_by(VisitRequest.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        count_stmt = select(func.count()).select_from(VisitRequest)
        items = (await self.db.execute(stmt)).scalars().all()
        total = (await self.db.execute(count_stmt)).scalar_one()
        return list(items), total

    async def get(self, id: UUID) -> VisitRequest | None:
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        stmt = select(VisitRequest).options(joinedload(VisitRequest.assigned_user)).where(VisitRequest.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, request: VisitRequest, payload: dict) -> VisitRequest:
        for key, value in payload.items():
            setattr(request, key, value)
        await self.db.flush()
        return request

    async def delete(self, request: VisitRequest) -> None:
        await self.db.delete(request)
        await self.db.flush()

    async def count_by_status(self, status: str) -> int:
        from sqlalchemy import select, func
        stmt = select(func.count()).select_from(VisitRequest).where(VisitRequest.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one()
