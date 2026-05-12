from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.visit_request import VisitRequest
from app.repositories.visit_request_repository import VisitRequestRepository
from app.schemas.visit_request import VisitRequestCreate, VisitRequestUpdate

class VisitRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = VisitRequestRepository(db)

    async def create(self, payload: VisitRequestCreate) -> VisitRequest:
        request = VisitRequest(**payload.model_dump())
        await self.repo.create(request)
        await self.db.commit()
        return request

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[VisitRequest], int]:
        return await self.repo.list(limit, offset)

    async def update(self, id: UUID, payload: VisitRequestUpdate) -> VisitRequest:
        request = await self.repo.get(id)
        if not request:
            raise ValueError("Not found")
        await self.repo.update(request, payload.model_dump(exclude_unset=True))
        await self.db.commit()
        return request
