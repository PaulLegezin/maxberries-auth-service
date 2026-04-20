from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_config import logger
from app.core.security import get_pwd_hash
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse


class RegisterService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def register_user(self, user_in: UserCreate) -> UserResponse:
        logger.info("Запрос на регистрацию пользователя: %s", user_in.email)
        try:
            user_exists = await self.user_repo.exists_by_email(user_in.email)
            if user_exists:
                logger.warning(
                    "Пользователь с email: %s уже зарегистрирован", user_in.email
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже зарегистрирован",
                )

            role = await self.role_repo.get_by_name("user")
            if not role:
                logger.error("Роль 'user' не найдена в системе")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Роль 'user' не найдена в системе",
                )

            pwd_hash = get_pwd_hash(user_in.password)
            new_user = await self.user_repo.create_user(user_in, pwd_hash, role.id)

            logger.info("Пользователь успешно зарегистрирован: %s", new_user.email)
            return UserResponse(new_user)

        except HTTPException:
            raise

        except Exception as e:
            logger.error("Непредвиденная ошибка при регистрации: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера во время регистрации",
            ) from e
