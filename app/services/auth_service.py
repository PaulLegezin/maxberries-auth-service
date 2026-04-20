from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_config import logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_pwd,
)
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def authenticate_user(self, email: str, password: str) -> User:
        logger.info("Запрос на аутентификацию пользователя: %s", email)
        try:
            user = await self.user_repo.get_by_email_with_permissions(email)
            if not user or not verify_pwd(password, user.password_hash):
                logger.warning("Неудачная попытка входа, email: %s", email)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный email или пароль",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            logger.info("Пользователь успешно аутентифицирован: %s", email)
            return user

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Непредвиденная ошибка во время аутентификации: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера во время аутентификации",
            ) from e

    async def login(self, email: str, password: str) -> Token:
        user = await self.authenticate_user(email, password)
        permissions = [p.code for p in user.role.permissions] if user.role else []

        user_data = {
            "sub": str(user.id),
            "email": user.email,
            "permissions": permissions,
        }

        return Token(
            access_token=create_access_token(data=user_data),
            refresh_token=create_refresh_token(data=user_data),
            token_type="bearer",
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        logger.info("Запрос на обновление токена")
        try:
            token_data = decode_token(refresh_token)
            if not token_data:
                logger.warning(
                    "Использован недействительный или просроченный refresh token"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невалидный или просроченный refresh-токен",
                )

            user = await self.user_repo.get_by_id_with_permissions(token_data.user_id)
            if not user:
                logger.warning(
                    "Пользователь %s не найден во время обновления токена",
                    token_data.user_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден",
                )

            permissions = [p.code for p in user.role.permissions]
            new_data = {
                "sub": str(user.id),
                "email": user.email,
                "permissions": permissions,
                "role": user.role.name if user.role else None,
            }

            return Token(
                access_token=create_access_token(data=new_data),
                refresh_token=create_refresh_token(data=new_data),
                token_type="bearer",
            )
        except HTTPException:
            raise

        except Exception as e:
            logger.error("Непредвиденная ошибка при обновлении токена: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера во время обновления токена",
            ) from e
