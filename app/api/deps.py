import json
from typing import Annotated, Iterable
from uuid import UUID

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.property import PropertyFilter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DBSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except ValueError:
        raise creds_exc
    user_id_raw = payload.get("sub")
    if not user_id_raw:
        raise creds_exc
    try:
        user_id = UUID(str(user_id_raw))
    except ValueError:
        raise creds_exc
    user = await UserRepository(db).get(user_id)
    if not user or not user.is_active:
        raise creds_exc
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    allowed: Iterable[UserRole] = roles

    async def _checker(user: CurrentUser) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges",
            )
        return user

    return _checker


async def get_property_filters(
    request: Request,
    filter: str | None = Query(default=None, description="JSON string of filters"),
) -> PropertyFilter:
    # 1. Parse JSON if present
    data = {}
    if filter:
        try:
            data = json.loads(filter)
        except json.JSONDecodeError:
            pass  # Or raise HTTPException if you prefer strictness

    # 2. Merge with individual query params
    # We skip 'filter', 'limit', 'offset' as they are handled elsewhere
    skip_params = {"filter", "limit", "offset"}
    for key, value in request.query_params.items():
        if key not in skip_params and key in PropertyFilter.model_fields:
            data[key] = value

    return PropertyFilter.model_validate(data)
