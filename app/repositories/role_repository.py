from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permissions import Permission
from app.models.roles import Role
from app.schemas.role import RoleCreate


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[Role]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == name)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_or_create_default_role(self) -> Role:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == "user")
        )
        result = await self.session.execute(stmt)
        role = result.unique().scalar_one_or_none()
        if not role:
            role = Role(name="user", description="Default user role")
            self.session.add(role)
            await self.session.commit()
            return await self.get_by_id(role.id)
        return role

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_permissions(self) -> List[Role]:
        stmt = select(Role).options(selectinload(Role.permissions))
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def add_permission_to_role(self, role_id: int, permission_id: int) -> bool:
        try:
            stmt = (
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == role_id)
            )
            result = await self.session.execute(stmt)
            role = result.unique().scalar_one_or_none()

            permission = await self.session.get(Permission, permission_id)

            if role and permission:
                if permission not in role.permissions:
                    role.permissions.append(permission)
                    await self.session.commit()
                    return True
            return False

        except IntegrityError:
            await self.session.rollback()
            raise

    async def remove_permission_from_role(
        self, role_id: int, permission_id: int
    ) -> bool:
        try:
            stmt = (
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == role_id)
            )
            result = await self.session.execute(stmt)
            role = result.unique().scalar_one_or_none()

            if role:
                role.permissions = [
                    p for p in role.permissions if p.id != permission_id
                ]
                await self.session.commit()
                return True
            return False

        except IntegrityError:
            await self.session.rollback()
            raise

    async def delete_role(self, role_id: int) -> bool:
        try:
            stmt = delete(Role).where(Role.id == role_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0

        except IntegrityError:
            await self.session.rollback()
            raise

    async def create_role(self, role_data: RoleCreate) -> Role:
        try:
            new_role = Role(name=role_data.name, description=role_data.description)
            self.session.add(new_role)

            await self.session.commit()
            await self.session.refresh(new_role)
            return new_role

        except IntegrityError:
            await self.session.rollback()
            raise
