import uuid
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.roles import Role
from app.models.users import User
from app.schemas.user import UserCreateAdmin


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.session.get(User, user_id)

    async def get_default_role(self) -> Optional[Role]:
        role_stmt = select(Role).where(Role.name == "user")
        role_result = await self.session.execute(role_stmt)
        return role_result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None

    async def get_by_email_with_permissions(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(joinedload(User.role).joinedload(Role.permissions))
            .where(User.email == email)
        )

        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_id_with_permissions(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_all_users(self) -> List[User]:
        stmt = select(User).options(selectinload(User.role))
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def create_user(
        self, user_data: UserCreateAdmin, pwd_hash: str, role_id: int
    ) -> User:
        try:
            new_user = User(
                email=user_data.email,
                name=user_data.name,
                password_hash=pwd_hash,
                role_id=role_id,
            )

            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user

        except IntegrityError:
            await self.session.rollback()
            raise

    async def update_user(self, user_id: uuid.UUID, **kwargs) -> User:
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None

            for key, value in kwargs.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)

            await self.session.commit()
            await self.session.refresh(user)
            return user

        except IntegrityError:
            await self.session.rollback()
            raise

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        try:
            stmt = delete(User).where(User.id == user_id).returning(User.id)
            result = await self.session.execute(stmt)
            deleted_id = result.scalar_one_or_none()
            if deleted_id:
                await self.session.commit()
                return True
            return False

        except IntegrityError:
            await self.session.rollback()
            raise

    async def change_user_role(self, user_id: uuid.UUID, role_id: int) -> User:
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            user.role_id = role_id
            await self.session.commit()
            await self.session.refresh(user)
            return user

        except IntegrityError:
            await self.session.rollback()
            raise
