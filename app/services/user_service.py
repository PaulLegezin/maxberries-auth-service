import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_config import logger
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate


class UserManagementService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def get_all_users(self) -> List[UserResponse]:
        try:
            logger.info("Запрос на получение всех пользователей")
            users = await self.user_repo.get_all_users()
            logger.info("Успешно найдено пользователей: %s", len(users))
            return users

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске пользователей: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserResponse:
        try:
            logger.info("Запрос на получение пользователя. ID: %s", user_id)
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                logger.warning("Пользователь с ID: %s не найден", user_id)
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            logger.info("Пользователь успешно найден. ID: %s", user_id)
            return user

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске пользователея: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def get_user_by_email(self, email: str) -> UserResponse:
        try:
            logger.info("Запрос на получение пользователя. Email: %s", email)
            user = await self.user_repo.get_by_email(email)
            if not user:
                logger.warning("Пользователь с Email: %s не найден", email)
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            logger.info("Пользователь успешно найден. Email: %s", email)
            return user

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске пользователея: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def create_user(self, user_data, pwd_hash: str, role_id: int) -> UserResponse:
        try:
            logger.info("Запрос на создание нового пользователя")
            new_user = await self.user_repo.create_user(user_data, pwd_hash, role_id)
            logger.info("Пользователь успешно создан. ID: %s", new_user.id)
            return new_user
        except Exception as e:
            logger.exception(
                "Ошибка базы данных при создании пользователея: %s", str(e)
            )
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def update_user(
        self, user_id: uuid.UUID, user_data: UserUpdate
    ) -> UserResponse:
        try:
            logger.info("Запрос на обновление пользователя")
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            if user_data.role_id is not None:
                role = await self.role_repo.get_by_id(user_data.role_id)
                if not role:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Роль не найдена"
                    )

            if user_data.email and user_data.email != user.email:
                existing = await self.user_repo.get_by_email(user_data.email)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Пользователь с таким email уже существует",
                    )

            update_data = user_data.model_dump(exclude_unset=True)
            updated_user = await self.user_repo.update_user(user_id, **update_data)
            logger.info("Пользователь успешно обновлен. ID: %s", updated_user.id)
            return UserResponse.model_validate(updated_user)

        except HTTPException:
            raise

        except Exception as e:
            logger.exception(
                "Ошибка базы данных при обновлении пользователея: %s", str(e)
            )
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def delete_user(self, user_id: uuid.UUID):
        try:
            logger.info("Запрос на удаление пользователя")
            deleted_user = await self.user_repo.delete_user(user_id)
            if deleted_user is False:
                logger.warning("Пользователь с ID: %s не найден", user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь  не найден",
                )
            logger.info("Пользователь успешно обновлен. ID: %s", deleted_user)

        except HTTPException:
            raise

        except Exception as e:
            logger.exception(
                "Ошибка базы данных при удалении пользователея: %s", str(e)
            )
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def change_user_role(self, user_id: uuid.UUID, role_id: int) -> UserResponse:
        try:
            logger.info("Запрос на смену роли пользователя с ID: %s", user_id)

            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise HTTPException(status_code=404, detail="Роль не найдена")

            changed_user = await self.user_repo.change_user_role(
                user_id, role_id=role_id
            )
            if not changed_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден",
                )

            logger.info("Роль для пользователя с ID: %s изменена", user_id)
            return UserResponse.model_validate(changed_user)

        except HTTPException:
            raise

        except Exception as e:
            logger.exception(
                "Ошибка базы данных при смене роли пользователея: %s", str(e)
            )
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e
