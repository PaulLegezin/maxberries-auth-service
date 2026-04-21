from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_config import logger
from app.repositories.permission_repository import PermissionRepository
from app.schemas.permission import PermissionCreate, PermissionResponse


class PermissionManagementService:
    def __init__(self, db: AsyncSession):
        self.permission_repo = PermissionRepository(db)

    async def get_all_permissions(self) -> List[PermissionResponse]:
        try:
            logger.info("Запрос на получение разрешений")
            permissions = await self.permission_repo.get_all()
            logger.info("Успешно найдено разрешений: %s", len(permissions))
            return permissions

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске разрешений: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def get_by_id(self, permission_id: int) -> PermissionResponse:
        try:
            logger.info("Запрос на получение разрешения. ID: %s", permission_id)
            permission = await self.permission_repo.get_by_id(permission_id)
            if not permission:
                raise HTTPException(status_code=404, detail="Разрешение не найдено")

            logger.info("Разрешение успешно найдено. ID: %s", permission_id)
            return permission

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске разрешения: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def get_by_code(self, code: str) -> PermissionResponse:
        try:
            logger.info("Запрос на получение разрешения. Code: %s", code)
            permission = await self.permission_repo.get_by_code(code)
            if not permission:
                raise HTTPException(status_code=404, detail="Разрешение не найдено")

            logger.info("Разрешение успешно найдено. ID: %s", code)
            return permission

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при поиске разрешения: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def create_permission(
        self, permission_data: PermissionCreate
    ) -> PermissionResponse:
        try:
            logger.info("Запрос на создание разрешения")
            existing = await self.permission_repo.get_by_code(permission_data.code)
            if existing:
                raise HTTPException(
                    status_code=400, detail="Разрешение с таким кодом уже существует"
                )

            new_permission = await self.permission_repo.create(permission_data)
            logger.info("Разрешение %s успешно создана", permission_data.code)
            return new_permission

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при создании разрешения: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def update_permission(
        self, permission_id: int, permission_data: PermissionCreate
    ) -> PermissionResponse:
        try:
            logger.info("Запрос на изменение разрешения")
            existing = await self.permission_repo.get_by_id(permission_id)
            if not existing:
                raise HTTPException(status_code=400, detail="Разрешение не найдено")

            updated_permissin = await self.permission_repo.update(
                permission_id, permission_data
            )
            return updated_permissin

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при изменении разрешения: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e

    async def delete_permission(self, permission_id: int):
        try:
            logger.info("Запрос на удаление разрешения")
            is_deleted = await self.permission_repo.delete(permission_id)
            if is_deleted is False:
                raise HTTPException(status_code=400, detail="Разрешение не найдено")

            logger.info("Разрешение успешно удалено. ID: %s", permission_id)

        except HTTPException:
            raise

        except Exception as e:
            logger.exception("Ошибка базы данных при удалении разрешения: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            ) from e
