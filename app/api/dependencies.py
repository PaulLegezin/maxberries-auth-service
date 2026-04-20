from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload

from app.core.db import engine
from app.core.security import decode_token
from app.models.users import User
from app.schemas.token import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as db:
        yield db


def get_current_user_data(token: str = Depends(oauth2_scheme)) -> TokenData:

    token_data = decode_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен или срок действия истек",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


def check_permission(required_permission: str):
    def permission_dependency(token_data: TokenData = Depends(get_current_user_data)):
        if required_permission not in token_data.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется: {required_permission}",
            )
        return True

    return permission_dependency


async def get_current_user(
    token_data: TokenData = Depends(get_current_user_data),
    db: AsyncSession = Depends(get_db),
):

    stmt = (
        select(User).options(joinedload(User.role)).where(User.id == token_data.user_id)
    )
    result = await db.execute(stmt)
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


async def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас недостаточно прав для выполнения этого действия",
        )
    return current_user
