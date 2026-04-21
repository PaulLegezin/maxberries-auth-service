from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_config import logger
from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate, RoleResponse


class RoleManagementService:
    def __init__(self, db: AsyncSession):
        self.role_repo = RoleRepository(db)

    async def get_all_roles_with_permissions(self) -> List[RoleResponse]:
        try:
            logger.info("Запрос на получение всех ролей")
            roles = await self.role_repo.get_all_with_permissions()
            logger.info("Успешно найдено ролей: %s", len(roles))
            return roles

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске ролей: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def get_role_by_id(self, role_id: int) -> RoleResponse:
        try:
            logger.info("Запрос на получение роли. ID: %s", role_id)
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise HTTPException(status_code=404, detail="Роль не найдена")

            logger.info("Роль успешно найдена. ID: %s", role_id)
            return role

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске роли: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def get_role_by_name(self, name: str) -> RoleResponse:
        try:
            logger.info("Запрос на получение роли. Имя: %s", name)
            role = await self.role_repo.get_by_name(name)
            if not role:
                raise HTTPException(status_code=404, detail="Роль не найдена")

            logger.info("Роль успешно найдена. Имя: %s", name)
            return role

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске роли: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def get_or_create_default_role(self) -> RoleResponse:
        try:
            logger.info("Запрос на получение или создание дефолтной роли")
            role = await self.role_repo.get_or_create_default_role()
            logger.info(
                "Запрос на получение или создание дефолтной роли успешно выполнен"
            )
            return role

        except HTTPException:
            raise

        except Exception as e:
            logger.exception(
                "Ошибка базы данных при поиске или создании роли: %s", str(e)
            )
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        try:
            logger.info("Запрос на создание роли: %s", role_data.name)
            existing = await self.role_repo.get_by_name(role_data.name)
            if existing:
                raise HTTPException(
                    status_code=400, detail="Роль с таким именем уже существует"
                )

            role = await self.role_repo.create_role(role_data)
            logger.info("Роль %s успешно создана", role_data.name)
            return role

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при создании роли: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def add_permission_to_role(self, role_id: int, permission_id: int):
        try:
            logger.info("Запрос на добавление разрешния в роль. ID: %s", role_id)
            is_added = await self.role_repo.add_permission_to_role(
                role_id, permission_id
            )
            if is_added is False:
                logger.warning("Роль или разрешение не найдены")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Роль или разрешение не найдены",
                )
            logger.info("Разрешение успешно добавлено. ID: %s", permission_id)

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при добавлении разрешния: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def remove_permission_from_role(self, role_id: int, permission_id: int):
        try:
            logger.info("Запрос на удаление разрешния из роли. ID: %s", role_id)
            is_removed = await self.role_repo.remove_permission_from_role(
                role_id, permission_id
            )
            if is_removed is False:
                logger.warning("Разрешение не найдено")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Разрешение не найдено",
                )
            logger.info("Разрешение успешно удалено. ID: %s", permission_id)

        except HTTPException:
            raise

        except Exception as e:
            logger.exception(
                "Ошибка базы данных при удалении разрешния из роли: %s", str(e)
            )
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def delete_role(self, role_id: int):
        try:
            logger.info("Запрос на удаление роли")
            is_deleted = await self.role_repo.delete_role(role_id)
            if is_deleted is False:
                logger.warning("Роль не найдена")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Роль не найдена"
                )
            logger.info("Роль успешно удалена. ID: %s", role_id)

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при удалении роли: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e
