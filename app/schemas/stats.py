from pydantic import BaseModel


class DashboardKPI(BaseModel):
    value: int
    trend_value: str | None = None
    trend_positive: bool = True


class DashboardStats(BaseModel):
    total_properties: DashboardKPI
    pending_validation: DashboardKPI
    scheduled_visits: DashboardKPI
    property_views: DashboardKPI
