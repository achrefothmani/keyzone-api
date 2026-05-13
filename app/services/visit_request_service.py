from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.visit_request import VisitRequest
from app.repositories.visit_request_repository import VisitRequestRepository
from app.schemas.visit_request import VisitRequestCreate, VisitRequestUpdate

class VisitRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = VisitRequestRepository(db)

    async def create(self, payload: VisitRequestCreate, source: str = "website") -> VisitRequest:
        request = VisitRequest(**payload.model_dump(), source=source)
        await self.repo.create(request)
        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[VisitRequest], int]:
        return await self.repo.list(limit, offset)

    async def update(self, id: UUID, payload: VisitRequestUpdate) -> VisitRequest:
        request = await self.repo.get(id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit request not found")
        await self.repo.update(request, payload.model_dump(exclude_unset=True))
        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def delete(self, id: UUID) -> None:
        request = await self.repo.get(id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit request not found")
        await self.repo.delete(request)
        await self.db.commit()
