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
        stmt = select(VisitRequest).order_by(VisitRequest.created_at.desc()).limit(limit).offset(offset)
        count_stmt = select(func.count()).select_from(VisitRequest)
        items = (await self.db.execute(stmt)).scalars().all()
        total = (await self.db.execute(count_stmt)).scalar_one()
        return list(items), total

    async def get(self, id: UUID) -> VisitRequest | None:
        return await self.db.get(VisitRequest, id)

    async def update(self, request: VisitRequest, payload: dict) -> VisitRequest:
        for key, value in payload.items():
            setattr(request, key, value)
        await self.db.flush()
        return request
