from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    images,
    properties,
    public,
    stats,
    users,
    visit_requests,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(properties.router)
api_router.include_router(images.router)
api_router.include_router(stats.router)
api_router.include_router(visit_requests.router)
api_router.include_router(public.router)
