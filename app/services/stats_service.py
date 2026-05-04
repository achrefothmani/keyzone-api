from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.property_repository import PropertyRepository
from app.schemas.stats import DashboardStats, DashboardKPI

class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.property_repo = PropertyRepository(db)

    async def get_dashboard_stats(self) -> DashboardStats:
        total = await self.property_repo.count_total()
        pending = await self.property_repo.count_by_validation("En attente de validation")
        
        return DashboardStats(
            total_properties=DashboardKPI(value=total),
            pending_validation=DashboardKPI(value=pending)
        )
