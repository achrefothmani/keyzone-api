from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DBSession, require_roles
from app.models.user import UserRole
from app.schemas.common import Page
from app.schemas.user import UserCreate, UserFilter, UserOut, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

admin_only = Depends(require_roles(UserRole.CHEF_AGENCE))


@router.get("", response_model=Page[UserOut])
async def list_users(
    db: DBSession,
    _: CurrentUser,
    zone: str | None = None,
    role: UserRole | None = None,
    search: str | None = None,
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> Page[UserOut]:
    items, total = await UserService(db).list(
        UserFilter(zone=zone, role=role, search=search), limit, offset
    )
    return Page[UserOut](
        items=[UserOut.model_validate(u) for u in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_only],
)
async def create_user(payload: UserCreate, db: DBSession) -> UserOut:
    user = await UserService(db).create(payload)
    return UserOut.model_validate(user)


@router.get("/{user_id}", response_model=UserOut, dependencies=[admin_only])
async def get_user(user_id: UUID, db: DBSession, _: CurrentUser) -> UserOut:
    user = await UserService(db).get(user_id)
    return UserOut.model_validate(user)


@router.put("/{user_id}", response_model=UserOut, dependencies=[admin_only])
async def update_user(user_id: UUID, payload: UserUpdate, db: DBSession) -> UserOut:
    user = await UserService(db).update(user_id, payload)
    return UserOut.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[admin_only],
)
async def delete_user(user_id: UUID, db: DBSession) -> None:
    await UserService(db).delete(user_id)
