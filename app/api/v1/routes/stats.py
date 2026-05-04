from fastapi import APIRouter, Depends
from app.api.deps import CurrentUser, DBSession
from app.schemas.stats import DashboardStats
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: DBSession, _: CurrentUser) -> DashboardStats:
    return await StatsService(db).get_dashboard_stats()
