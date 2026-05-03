from fastapi import APIRouter

from app.api.v1.routes import auth, images, properties, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(properties.router)
api_router.include_router(images.router)
