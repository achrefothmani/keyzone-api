from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.property_repository import PropertyRepository
from app.repositories.visit_request_repository import VisitRequestRepository
from app.models.property import PropertyValidationStatus
from app.schemas.stats import DashboardStats, DashboardKPI
from app.core.config import settings

class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.property_repo = PropertyRepository(db)
        self.visit_repo = VisitRequestRepository(db)

    async def get_dashboard_stats(self) -> DashboardStats:
        total = await self.property_repo.count_total()
        pending = await self.property_repo.count_by_validation(PropertyValidationStatus.PENDING)
        
        # Get pending visit requests (mapped to "En attente" in UI)
        scheduled_visits = await self.visit_repo.count_by_status("pending")
        
        # Get views from Umami
        property_views = await self._get_umami_views()
        
        return DashboardStats(
            total_properties=DashboardKPI(value=total),
            pending_validation=DashboardKPI(value=pending),
            scheduled_visits=DashboardKPI(value=scheduled_visits),
            property_views=DashboardKPI(value=property_views)
        )

    async def _get_umami_views(self) -> int:
        if not settings.async_umami_database_url or not settings.UMAMI_WEBSITE_ID:
            return 0
        
        try:
            from sqlalchemy import create_async_engine, text
            # Use a one-off engine for the Umami database
            # In a high-traffic scenario, this should be a singleton engine/pool
            engine = create_async_engine(settings.async_umami_database_url)
            async with engine.connect() as conn:
                # event_type 1 is pageview in Umami
                query = text("""
                    SELECT count(*) 
                    FROM website_event 
                    WHERE website_id = :website_id 
                    AND event_type = 1 
                    AND url_path LIKE '/proprietes/%'
                    AND created_at >= NOW() - INTERVAL '30 days'
                """)
                result = await conn.execute(query, {"website_id": settings.UMAMI_WEBSITE_ID})
                count = result.scalar()
            await engine.dispose()
            return count or 0
        except Exception as e:
            # Silently fail for stats to avoid breaking the whole dashboard
            return 0
