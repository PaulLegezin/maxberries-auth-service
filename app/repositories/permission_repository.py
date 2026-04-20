from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permissions import Permission
from app.schemas.permission import PermissionCreate


class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, permission_id: int) -> Optional[Permission]:
        return await self.session.get(Permission, permission_id)

    async def get_by_code(self, code: str) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Permission]:
        stmt = select(Permission).options(selectinload(Permission.roles))
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def create(self, permission_data: PermissionCreate) -> Permission:
        try:
            new_permission = Permission(
                code=permission_data.code, description=permission_data.description
            )
            self.session.add(new_permission)

            await self.session.commit()
            await self.session.refresh(new_permission)
            return new_permission

        except IntegrityError:
            await self.session.rollback()
            raise

    async def update(
        self, permission_id: int, permission_data: PermissionCreate
    ) -> Optional[Permission]:
        try:
            permission = await self.session.get(Permission, permission_id)
            if not permission:
                return None

            for key, value in permission_data.model_dump(exclude_unset=True).items():
                setattr(permission, key, value)

            await self.session.commit()
            await self.session.refresh(permission)
            return permission

        except IntegrityError:
            await self.session.rollback()
            raise

    async def delete(self, permission_id: int) -> bool:
        try:
            stmt = delete(Permission).where(Permission.id == permission_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0

        except IntegrityError:
            await self.session.rollback()
            raise
