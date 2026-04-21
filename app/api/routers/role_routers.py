from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import admin_required, check_permission, get_db
from app.schemas.role import RoleCreate, RoleResponse
from app.services.role_service import RoleManagementService

router = APIRouter(
    prefix="/role",
    tags=["Role"],
    dependencies=[Depends(admin_required), Depends(check_permission("role.access"))],
)


@router.get("/default", response_model=RoleResponse)
async def get_or_create_default_role(
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:

    service = RoleManagementService(db)
    role = await service.get_or_create_default_role()
    return role


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role_by_id(
    role_id: int, db: AsyncSession = Depends(get_db)
) -> RoleResponse:

    service = RoleManagementService(db)
    role = await service.get_role_by_id(role_id)
    return role


@router.get("/name/{name}", response_model=RoleResponse)
async def get_role_by_name(
    name: str, db: AsyncSession = Depends(get_db)
) -> RoleResponse:

    service = RoleManagementService(db)
    role = await service.get_role_by_name(name)
    return role


@router.get("/", response_model=List[RoleResponse])
async def get_all_roles_with_permissions(
    db: AsyncSession = Depends(get_db),
) -> List[RoleResponse]:

    service = RoleManagementService(db)
    roles = await service.get_all_roles_with_permissions()
    return roles


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    role_data: RoleCreate, db: AsyncSession = Depends(get_db)
) -> RoleResponse:

    service = RoleManagementService(db)
    new_role = await service.create_role(role_data)
    return new_role


@router.patch("/add_permission/{role_id}", status_code=204)
async def add_permission_to_role(
    role_id: int, permission_id: int, db: AsyncSession = Depends(get_db)
):

    service = RoleManagementService(db)
    await service.add_permission_to_role(role_id, permission_id)
    return None


@router.patch("/remove_permission/{role_id}", status_code=204)
async def remove_permission_from_role(
    role_id: int, permission_id: int, db: AsyncSession = Depends(get_db)
):

    service = RoleManagementService(db)
    await service.remove_permission_from_role(role_id, permission_id)
    return None


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):

    service = RoleManagementService(db)
    await service.delete_role(role_id)
    return None
