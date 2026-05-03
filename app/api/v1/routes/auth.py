from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DBSession
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.schemas.user import UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: DBSession) -> Token:
    return await AuthService(db).login(payload)


@router.post("/login/form", response_model=Token, include_in_schema=False)
async def login_form(
    db: DBSession,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """OAuth2 password flow (used by Swagger's `Authorize` button)."""
    return await AuthService(db).login(
        LoginRequest(email=form.username, password=form.password)
    )


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: RegisterRequest, db: DBSession) -> UserOut:
    user = await AuthService(db).register(payload)
    return UserOut.model_validate(user)


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
