from sqlalchemy.ext.asyncio import AsyncSession
from app.models.visit_request import VisitRequest
from app.repositories.visit_request_repository import VisitRequestRepository
from app.schemas.visit_request import VisitRequestCreate

class VisitRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = VisitRequestRepository(db)

    async def create(self, payload: VisitRequestCreate) -> VisitRequest:
        request = VisitRequest(**payload.model_dump())
        await self.repo.create(request)
        await self.db.commit()
        return request
