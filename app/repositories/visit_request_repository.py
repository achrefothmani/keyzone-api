from sqlalchemy.ext.asyncio import AsyncSession
from app.models.visit_request import VisitRequest

class VisitRequestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, request: VisitRequest) -> VisitRequest:
        self.db.add(request)
        await self.db.flush()
        return request
