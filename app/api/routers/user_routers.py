import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import admin_required, get_db
from app.core.security import get_pwd_hash
from app.schemas.user import UserCreateAdmin, UserResponse, UserUpdate
from app.services.user_service import UserManagementService

router = APIRouter(
    prefix="/user", tags=["User"], dependencies=[Depends(admin_required)]
)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> UserResponse:

    service = UserManagementService(db)
    user = await service.get_user_by_id(user_id)
    return user


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str, db: AsyncSession = Depends(get_db)
) -> UserResponse:

    service = UserManagementService(db)
    user = await service.get_user_by_email(email)
    return user


@router.get("/", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)) -> List[UserResponse]:

    service = UserManagementService(db)
    users = await service.get_all_users()
    return users


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreateAdmin, db: AsyncSession = Depends(get_db)
) -> UserResponse:

    pwd_hash = get_pwd_hash(user_data.password)
    role_id = user_data.role_id
    service = UserManagementService(db)
    new_user = await service.create_user(user_data, pwd_hash, role_id)
    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID, user_data: UserUpdate, db: AsyncSession = Depends(get_db)
) -> UserResponse:

    service = UserManagementService(db)
    updated_user = await service.update_user(user_id, user_data=user_data)
    return updated_user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):

    service = UserManagementService(db)
    await service.delete_user(user_id)
    return None


@router.patch("/user_role/{user_id}", response_model=UserResponse)
async def change_user_role(
    user_id: uuid.UUID, role_id: int, db: AsyncSession = Depends(get_db)
) -> UserResponse:

    service = UserManagementService(db)
    updated_user = await service.change_user_role(user_id, role_id=role_id)
    return updated_user
