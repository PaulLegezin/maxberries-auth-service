from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.token import Token, TokenUpdate
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.register_service import RegisterService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:

    service = RegisterService(db)
    return await service.register_user(user_in)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Token:

    service = AuthService(db)
    return await service.login(email=form_data.username, password=form_data.password)


@router.get("/me", response_model=UserResponse)
async def read_users_me(user: User = Depends(get_current_user)):
    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(data: TokenUpdate, db: AsyncSession = Depends(get_db)):

    service = AuthService(db)
    return await service.refresh_access_token(data.refresh_token)
